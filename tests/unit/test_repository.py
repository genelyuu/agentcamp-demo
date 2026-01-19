"""
tests/unit/test_repository.py - BaseJSONRepository 단위 테스트
TEST-011: Repository 패턴 테스트
"""
import pytest
import os
import tempfile
from typing import List

from pydantic import BaseModel, Field

from core.repository import BaseJSONRepository


# 테스트용 Pydantic 모델
class SampleItem(BaseModel):
    """테스트용 아이템 모델"""
    id: str
    name: str
    value: int = 0


class SampleContainer(BaseModel):
    """테스트용 컨테이너 모델"""
    items: List[SampleItem] = Field(default_factory=list)


class TestBaseJSONRepository:
    """BaseJSONRepository 테스트"""

    @pytest.fixture
    def temp_path(self, tmp_path):
        """임시 파일 경로 픽스처"""
        return str(tmp_path / "test_data.json")

    @pytest.fixture
    def repo(self, temp_path):
        """Repository 픽스처"""
        return BaseJSONRepository[SampleItem](
            path=temp_path,
            container_cls=SampleContainer,
            item_key="items"
        )

    @pytest.fixture
    def sample_item(self):
        """샘플 아이템 픽스처"""
        return SampleItem(id="test-001", name="테스트 아이템", value=100)

    def test_ensure_file_creates_directory(self, tmp_path):
        """디렉토리 생성 테스트"""
        nested_path = str(tmp_path / "nested" / "dir" / "test.json")
        repo = BaseJSONRepository[SampleItem](
            path=nested_path,
            container_cls=SampleContainer,
            item_key="items"
        )
        repo._ensure_file()
        assert os.path.exists(nested_path)

    def test_ensure_file_creates_empty_file(self, repo, temp_path):
        """빈 파일 생성 테스트"""
        repo._ensure_file()
        assert os.path.exists(temp_path)

    def test_get_all_empty(self, repo):
        """빈 리스트 조회 테스트"""
        result = repo.get_all()
        assert isinstance(result, list)
        assert len(result) == 0

    def test_create_item(self, repo, sample_item):
        """아이템 생성 테스트"""
        result = repo.create(sample_item)
        assert result.id == sample_item.id
        assert result.name == sample_item.name

    def test_get_all_after_create(self, repo, sample_item):
        """생성 후 조회 테스트"""
        repo.create(sample_item)
        result = repo.get_all()
        assert len(result) == 1
        assert result[0].id == sample_item.id

    def test_get_by_id(self, repo, sample_item):
        """ID로 조회 테스트"""
        repo.create(sample_item)
        result = repo.get_by_id("test-001")
        assert result is not None
        assert result.id == "test-001"

    def test_get_by_id_not_found(self, repo):
        """존재하지 않는 ID 조회 테스트"""
        result = repo.get_by_id("nonexistent")
        assert result is None

    def test_get_by_id_custom_field(self, repo, sample_item):
        """커스텀 ID 필드로 조회 테스트"""
        repo.create(sample_item)
        result = repo.get_by_id("테스트 아이템", id_field="name")
        assert result is not None
        assert result.name == "테스트 아이템"

    def test_update_item(self, repo, sample_item):
        """아이템 업데이트 테스트"""
        repo.create(sample_item)
        result = repo.update("test-001", {"name": "업데이트된 이름", "value": 200})
        assert result is not None
        assert result.name == "업데이트된 이름"
        assert result.value == 200

    def test_update_item_not_found(self, repo):
        """존재하지 않는 아이템 업데이트 테스트"""
        result = repo.update("nonexistent", {"name": "새 이름"})
        assert result is None

    def test_delete_item(self, repo, sample_item):
        """아이템 삭제 테스트"""
        repo.create(sample_item)
        result = repo.delete("test-001")
        assert result is True

        # 삭제 확인
        assert repo.get_by_id("test-001") is None

    def test_delete_item_not_found(self, repo):
        """존재하지 않는 아이템 삭제 테스트"""
        result = repo.delete("nonexistent")
        assert result is False

    def test_filter(self, repo):
        """필터링 테스트"""
        repo.create(SampleItem(id="item-1", name="아이템1", value=50))
        repo.create(SampleItem(id="item-2", name="아이템2", value=150))
        repo.create(SampleItem(id="item-3", name="아이템3", value=100))

        result = repo.filter(lambda x: x.value >= 100)
        assert len(result) == 2

    def test_count_all(self, repo):
        """전체 개수 테스트"""
        repo.create(SampleItem(id="item-1", name="아이템1", value=50))
        repo.create(SampleItem(id="item-2", name="아이템2", value=150))

        result = repo.count()
        assert result == 2

    def test_count_with_predicate(self, repo):
        """조건부 개수 테스트"""
        repo.create(SampleItem(id="item-1", name="아이템1", value=50))
        repo.create(SampleItem(id="item-2", name="아이템2", value=150))
        repo.create(SampleItem(id="item-3", name="아이템3", value=100))

        result = repo.count(lambda x: x.value > 75)
        assert result == 2

    def test_multiple_operations(self, repo):
        """복합 작업 테스트"""
        # 생성
        repo.create(SampleItem(id="item-1", name="첫번째", value=10))
        repo.create(SampleItem(id="item-2", name="두번째", value=20))

        # 업데이트
        repo.update("item-1", {"value": 15})

        # 삭제
        repo.delete("item-2")

        # 확인
        all_items = repo.get_all()
        assert len(all_items) == 1
        assert all_items[0].id == "item-1"
        assert all_items[0].value == 15


class TestRepositoryPersistence:
    """Repository 영속성 테스트"""

    def test_data_persists_across_instances(self, tmp_path):
        """인스턴스 간 데이터 영속성 테스트"""
        path = str(tmp_path / "persist_test.json")

        # 첫 번째 인스턴스에서 데이터 생성
        repo1 = BaseJSONRepository[SampleItem](
            path=path,
            container_cls=SampleContainer,
            item_key="items"
        )
        repo1.create(SampleItem(id="persist-001", name="영속성 테스트", value=999))

        # 두 번째 인스턴스에서 데이터 조회
        repo2 = BaseJSONRepository[SampleItem](
            path=path,
            container_cls=SampleContainer,
            item_key="items"
        )
        result = repo2.get_by_id("persist-001")

        assert result is not None
        assert result.name == "영속성 테스트"
        assert result.value == 999

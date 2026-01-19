"""
core/repository.py - JSON 파일 기반 Repository 베이스 클래스
DUP-002: 코드 중복 제거를 위한 공통 Repository
"""
import json
import os
from typing import TypeVar, Generic, List, Optional, Type, Callable
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class BaseJSONRepository(Generic[T]):
    """
    JSON 파일 기반 Repository 베이스 클래스

    risk.py, incident.py의 공통 패턴을 추출하여 DRY 원칙 준수

    Usage:
        repo = BaseJSONRepository(
            path="data/risks.json",
            container_cls=RiskRegister,
            item_key="risks"
        )
        all_items = repo.get_all()
    """

    def __init__(
        self,
        path: str,
        container_cls: Type[BaseModel],
        item_key: str,
        empty_container: Optional[dict] = None
    ):
        """
        Repository 초기화

        Args:
            path: JSON 파일 경로
            container_cls: 컨테이너 Pydantic 모델 클래스
            item_key: 컨테이너 내 아이템 리스트 키
            empty_container: 빈 컨테이너 초기값 (기본: {item_key: []})
        """
        self.path = path
        self.container_cls = container_cls
        self.item_key = item_key
        self.empty_container = empty_container or {item_key: []}

    def _ensure_file(self) -> None:
        """파일 존재 확인 및 생성"""
        dir_path = os.path.dirname(self.path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.empty_container, f, ensure_ascii=False, indent=2)

    def _load(self) -> BaseModel:
        """컨테이너 로드"""
        self._ensure_file()
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return self.container_cls(**data)

    def _save(self, container: BaseModel) -> None:
        """컨테이너 저장"""
        self._ensure_file()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(container.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

    def get_all(self) -> List[T]:
        """전체 아이템 조회"""
        container = self._load()
        return getattr(container, self.item_key)

    def get_by_id(self, item_id: str, id_field: str = "id") -> Optional[T]:
        """ID로 아이템 조회"""
        items = self.get_all()
        for item in items:
            if getattr(item, id_field, None) == item_id:
                return item
        return None

    def create(self, item: T) -> T:
        """아이템 생성"""
        container = self._load()
        items = getattr(container, self.item_key)
        items.append(item)
        self._save(container)
        return item

    def update(
        self,
        item_id: str,
        updates: dict,
        id_field: str = "id",
        item_cls: Optional[Type[T]] = None
    ) -> Optional[T]:
        """아이템 업데이트"""
        container = self._load()
        items = getattr(container, self.item_key)

        for i, item in enumerate(items):
            if getattr(item, id_field, None) == item_id:
                # 기존 데이터에 업데이트 적용
                item_dict = item.model_dump()
                item_dict.update(updates)

                # 새 객체 생성 (item_cls가 없으면 동일 타입 사용)
                cls = item_cls or type(item)
                updated_item = cls(**item_dict)
                items[i] = updated_item
                self._save(container)
                return updated_item

        return None

    def delete(self, item_id: str, id_field: str = "id") -> bool:
        """아이템 삭제"""
        container = self._load()
        items = getattr(container, self.item_key)
        original_count = len(items)

        # 필터링하여 새 리스트 생성
        filtered = [
            item for item in items
            if getattr(item, id_field, None) != item_id
        ]
        setattr(container, self.item_key, filtered)

        if len(filtered) < original_count:
            self._save(container)
            return True
        return False

    def filter(self, predicate: Callable[[T], bool]) -> List[T]:
        """조건에 맞는 아이템 필터링"""
        items = self.get_all()
        return [item for item in items if predicate(item)]

    def count(self, predicate: Optional[Callable[[T], bool]] = None) -> int:
        """아이템 개수 (조건부)"""
        items = self.get_all()
        if predicate:
            return len([item for item in items if predicate(item)])
        return len(items)

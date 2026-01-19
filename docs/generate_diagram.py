"""
AgentCamp v1.2 Architecture Diagram Generator
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

# Set up the figure
fig, ax = plt.subplots(1, 1, figsize=(18, 22))
ax.set_xlim(0, 18)
ax.set_ylim(0, 22)
ax.set_aspect('equal')
ax.axis('off')
fig.patch.set_facecolor('#FAFAFA')

# Colors
colors = {
    'ui': '#E3F2FD',
    'ui_border': '#1565C0',
    'facade': '#FFF8E1',
    'facade_border': '#F57F17',
    'core': '#E8F5E9',
    'core_border': '#2E7D32',
    'llm': '#F3E5F5',
    'llm_border': '#7B1FA2',
    'data': '#ECEFF1',
    'data_border': '#455A64',
    'cross': '#FFEBEE',
    'cross_border': '#C62828',
}

def draw_layer(ax, x, y, w, h, title, color, border_color, subtitle=''):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.4",
                          facecolor=color, edgecolor=border_color, linewidth=3)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h - 0.35, title, ha='center', va='top',
            fontsize=13, fontweight='bold', color=border_color)
    if subtitle:
        ax.text(x + w/2, y + h - 0.75, subtitle, ha='center', va='top',
                fontsize=9, color=border_color, style='italic')

def draw_box(ax, x, y, w, h, text, facecolor='white', edgecolor='gray', fontsize=9):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.15",
                          facecolor=facecolor, edgecolor=edgecolor, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=fontsize, wrap=True, linespacing=1.2)

def draw_arrow(ax, start, end, color='#37474F', style='->', lw=2):
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                               connectionstyle="arc3,rad=0"))

def draw_dashed_arrow(ax, start, end, color='#78909C'):
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5,
                               linestyle='dashed'))

# ============= TITLE =============
ax.text(9, 21.5, 'AgentCamp v1.2 Architecture', ha='center', va='center',
        fontsize=20, fontweight='bold', color='#1A237E')
ax.text(9, 21, 'AI-Powered OJT Platform with Digital Twin Agents', ha='center', va='center',
        fontsize=11, color='#5C6BC0', style='italic')

# ============= PRESENTATION LAYER =============
draw_layer(ax, 0.5, 18, 17, 2.5, 'PRESENTATION LAYER', colors['ui'], colors['ui_border'])

draw_box(ax, 6, 18.4, 6, 1.5, 'app.py\n(Streamlit UI)', '#BBDEFB', colors['ui_border'])
draw_box(ax, 1, 18.6, 1.5, 1, 'Admin\nMode', '#E3F2FD', colors['ui_border'])
draw_box(ax, 2.7, 18.6, 1.7, 1, 'NewHire\nMode', '#E3F2FD', colors['ui_border'])
draw_box(ax, 4.6, 18.6, 1.2, 1, 'Dash', '#E3F2FD', colors['ui_border'])
draw_box(ax, 12.3, 18.6, 1.7, 1, 'Settings', '#E3F2FD', colors['ui_border'])
draw_box(ax, 14.2, 18.6, 2.8, 1, 'LLM Config\n(Mock/Claude/OpenAI)', '#E3F2FD', colors['ui_border'])

# ============= FACADE LAYER =============
draw_layer(ax, 0.5, 15, 17, 2.5, 'API BOUNDARY', colors['facade'], colors['facade_border'], 'ADR-101: UI/Core Separation')

draw_box(ax, 5, 15.4, 8, 1.6, 'AgentCampAPI (Facade)\ncore/api.py\n' + '-'*25 + '\nSingle entry point for all business logic',
         '#FFE082', colors['facade_border'])

# ============= BUSINESS LOGIC LAYER =============
draw_layer(ax, 0.5, 9.5, 17, 5, 'BUSINESS LOGIC LAYER', colors['core'], colors['core_border'])

# Orchestrator
draw_box(ax, 1, 11.8, 4.5, 2.2, 'Orchestrator\ncore/orchestrator.py\n' + '-'*15 + '\nroute_question()\nanswer_question()',
         '#C8E6C9', colors['core_border'])

# Evaluation
draw_box(ax, 6, 11.8, 4.5, 2.2, 'Evaluation\ncore/evaluation.py\n' + '-'*15 + '\nevaluate_submission()\nevaluate_task()',
         '#C8E6C9', colors['core_border'])

# Risk Management
draw_box(ax, 11, 11.8, 5.5, 2.2, 'Risk Management\ncore/risk.py + incident.py\n' + '-'*15 + '\nRisk Register CRUD\nIncident Logging',
         '#C8E6C9', colors['core_border'])

# Cross-cutting
draw_box(ax, 1, 9.8, 16, 1.5,
         'Cross-Cutting:   logger.py (Loguru)  |  errors.py (Sentry)  |  repository.py (DRY)  |  schemas/ (Pydantic)',
         colors['cross'], colors['cross_border'], fontsize=10)

# ============= LLM CAPABILITY LAYER =============
draw_layer(ax, 0.5, 4.5, 17, 4.5, 'LLM CAPABILITY LAYER', colors['llm'], colors['llm_border'], 'ADR-104: Protocol-based Interface')

# Protocols
ax.text(9, 8.5, 'Capability Protocols (core/llm/protocols.py)', ha='center', va='center',
        fontsize=10, fontweight='bold', color=colors['llm_border'])

draw_box(ax, 1, 6.8, 3.5, 1.3, 'RouterCapability\nroute(q) -> twin', '#E1BEE7', colors['llm_border'])
draw_box(ax, 5, 6.8, 3.5, 1.3, 'AnswererCapability\nanswer(...) -> str', '#E1BEE7', colors['llm_border'])
draw_box(ax, 9, 6.8, 3.5, 1.3, 'ExtractorCapability\nextract(txt) -> items', '#E1BEE7', colors['llm_border'])
draw_box(ax, 13, 6.8, 3.5, 1.3, 'JudgeCapability\njudge(t,s) -> score', '#E1BEE7', colors['llm_border'])

# Providers
ax.text(9, 6.3, 'Provider Implementations', ha='center', va='center',
        fontsize=10, fontweight='bold', color=colors['llm_border'])

draw_box(ax, 2, 4.9, 3.5, 1.1, 'MockProvider\ncore/llm/mock.py', '#F3E5F5', colors['llm_border'])
draw_box(ax, 7, 4.9, 3.5, 1.1, 'ClaudeProvider\ncore/llm/claude.py', '#F3E5F5', colors['llm_border'])
draw_box(ax, 12, 4.9, 3.5, 1.1, 'OpenAIProvider\ncore/llm/openai.py', '#F3E5F5', colors['llm_border'])

# ============= DATA LAYER =============
draw_layer(ax, 0.5, 0.5, 17, 3.5, 'DATA LAYER', colors['data'], colors['data_border'])

# JSON Storage
ax.text(5, 3.5, 'JSON Storage (data/)', ha='center', va='center',
        fontsize=10, fontweight='bold', color=colors['data_border'])

draw_box(ax, 1, 1, 2, 1, 'org.json', '#CFD8DC', colors['data_border'])
draw_box(ax, 3.2, 1, 2.2, 1, 'knowledge\n.json', '#CFD8DC', colors['data_border'])
draw_box(ax, 5.6, 1, 2, 1, 'sessions\n.json', '#CFD8DC', colors['data_border'])
draw_box(ax, 7.8, 1, 2, 1, 'risks\n.json', '#CFD8DC', colors['data_border'])

# Digital Twins
ax.text(14, 3.5, 'Digital Twins (agents.py)', ha='center', va='center',
        fontsize=10, fontweight='bold', color=colors['data_border'])

draw_box(ax, 10.5, 2.2, 2.2, 1.1, 'Sam Lee\nCEO', '#B0BEC5', colors['data_border'])
draw_box(ax, 13, 2.2, 2.2, 1.1, 'JH Kim\nPM', '#B0BEC5', colors['data_border'])
draw_box(ax, 10.5, 0.9, 2.2, 1.1, 'Seul Kim\nFrontend', '#B0BEC5', colors['data_border'])
draw_box(ax, 13, 0.9, 2.2, 1.1, 'Jin Park\nBackend', '#B0BEC5', colors['data_border'])
draw_box(ax, 15.5, 1.5, 1.5, 1.1, 'incidents\n.json', '#CFD8DC', colors['data_border'])

# ============= ARROWS =============
# UI -> Facade
draw_arrow(ax, (9, 18.4), (9, 17.1))

# Facade -> Core (multiple outputs)
draw_arrow(ax, (7, 15.4), (3.25, 14.1))
draw_arrow(ax, (9, 15.4), (8.25, 14.1))
draw_arrow(ax, (11, 15.4), (13.75, 14.1))

# Core -> LLM
draw_arrow(ax, (3.25, 11.8), (2.75, 8.2))
draw_arrow(ax, (8.25, 11.8), (6.75, 8.2))
draw_arrow(ax, (8.25, 11.8), (10.75, 8.2))
draw_arrow(ax, (8.25, 11.8), (14.75, 8.2))

# Capabilities -> Providers
draw_arrow(ax, (2.75, 6.8), (3.75, 6.1))
draw_arrow(ax, (6.75, 6.8), (8.75, 6.1))
draw_arrow(ax, (14.75, 6.8), (13.75, 6.1))

# Core -> Data
draw_dashed_arrow(ax, (3.25, 9.8), (4.3, 4.1))
draw_dashed_arrow(ax, (13.75, 11.8), (13.75, 3.4))

# Legend
legend_y = 0.1
ax.text(0.7, legend_y, 'Legend:', fontsize=9, fontweight='bold')
draw_arrow(ax, (2.2, legend_y), (3, legend_y))
ax.text(3.2, legend_y, 'Data Flow', fontsize=8, va='center')
draw_dashed_arrow(ax, (5, legend_y), (5.8, legend_y))
ax.text(6, legend_y, 'Storage Access', fontsize=8, va='center')

plt.tight_layout()
plt.savefig('docs/architecture_v1.2.png', dpi=150, bbox_inches='tight',
            facecolor='#FAFAFA', edgecolor='none')
print("Architecture diagram saved to docs/architecture_v1.2.png")

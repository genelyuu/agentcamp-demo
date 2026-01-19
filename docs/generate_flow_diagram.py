"""
AgentCamp v1.2 Data Flow Diagram Generator
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import matplotlib.patches as mpatches

fig, axes = plt.subplots(3, 1, figsize=(16, 18))
fig.patch.set_facecolor('#FAFAFA')

colors = {
    'user': '#E3F2FD',
    'user_border': '#1565C0',
    'process': '#E8F5E9',
    'process_border': '#2E7D32',
    'llm': '#F3E5F5',
    'llm_border': '#7B1FA2',
    'data': '#FFF8E1',
    'data_border': '#F57F17',
    'result': '#FFEBEE',
    'result_border': '#C62828',
}

def setup_ax(ax, title):
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=14, fontweight='bold', color='#1A237E', pad=10)

def draw_box(ax, x, y, w, h, text, facecolor, edgecolor, fontsize=9):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.2",
                          facecolor=facecolor, edgecolor=edgecolor, linewidth=2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fontsize, wrap=True)

def draw_arrow(ax, start, end, label='', color='#37474F'):
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle='->', color=color, lw=2))
    if label:
        mid = ((start[0] + end[0])/2, (start[1] + end[1])/2 + 0.2)
        ax.text(mid[0], mid[1], label, ha='center', va='bottom', fontsize=8, color=color)

# ============= FLOW 1: Question-Answer =============
ax1 = axes[0]
setup_ax(ax1, '1. Question-Answer Flow')

draw_box(ax1, 0.3, 1.5, 2, 2, 'User\nQuestion', colors['user'], colors['user_border'])
draw_box(ax1, 3.5, 1.5, 2.5, 2, 'AgentCampAPI\nroute_question()', colors['process'], colors['process_border'])
draw_box(ax1, 7, 1.5, 2.5, 2, 'Router\nCapability', colors['llm'], colors['llm_border'])
draw_box(ax1, 10.5, 2.5, 2, 1.5, 'Digital Twin\nSelection', colors['data'], colors['data_border'])
draw_box(ax1, 10.5, 0.5, 2, 1.5, 'Answerer\nCapability', colors['llm'], colors['llm_border'])
draw_box(ax1, 13.5, 1.5, 2, 2, 'Response\nto User', colors['result'], colors['result_border'])

draw_arrow(ax1, (2.3, 2.5), (3.5, 2.5))
draw_arrow(ax1, (6, 2.5), (7, 2.5), 'route()')
draw_arrow(ax1, (9.5, 2.5), (10.5, 3.25))
draw_arrow(ax1, (11.5, 2.5), (11.5, 2))
draw_arrow(ax1, (12.5, 1.25), (13.5, 2), 'answer()')

# Routing keywords
ax1.text(8.25, 4.2, 'Routing Keywords:', fontsize=9, fontweight='bold')
ax1.text(8.25, 3.8, 'Sam Lee: strategy, priority, customer', fontsize=8)
ax1.text(8.25, 3.5, 'JH Kim: requirements, scope, KPI', fontsize=8)
ax1.text(8.25, 3.2, 'Seul Kim: UI, UX, frontend, component', fontsize=8)
ax1.text(8.25, 2.9, 'Jin Park: default (backend)', fontsize=8, style='italic')

# ============= FLOW 2: Submission Evaluation =============
ax2 = axes[1]
setup_ax(ax2, '2. Submission Evaluation Flow')

draw_box(ax2, 0.3, 1.5, 2, 2, 'Submission\n+ Task', colors['user'], colors['user_border'])
draw_box(ax2, 3.5, 1.5, 2.5, 2, 'AgentCampAPI\nevaluate_task()', colors['process'], colors['process_border'])
draw_box(ax2, 7, 1.5, 2.5, 2, 'Judge\nCapability', colors['llm'], colors['llm_border'])
draw_box(ax2, 10.5, 2.5, 3, 1.5, 'Keyword\nMatching', colors['data'], colors['data_border'])
draw_box(ax2, 10.5, 0.5, 3, 1.5, 'Rubric\nScoring', colors['data'], colors['data_border'])
draw_box(ax2, 14, 1.5, 1.5, 2, 'Score\n+\nFeedback', colors['result'], colors['result_border'])

draw_arrow(ax2, (2.3, 2.5), (3.5, 2.5))
draw_arrow(ax2, (6, 2.5), (7, 2.5), 'judge()')
draw_arrow(ax2, (9.5, 2.8), (10.5, 3.25))
draw_arrow(ax2, (9.5, 2.2), (10.5, 1.25))
draw_arrow(ax2, (13.5, 3.25), (14, 2.8))
draw_arrow(ax2, (13.5, 1.25), (14, 2.2))

# Scoring details
ax2.text(7, 4.2, 'Evaluation Criteria:', fontsize=9, fontweight='bold')
ax2.text(7, 3.8, 'Base Score: 50 points', fontsize=8)
ax2.text(7, 3.5, '+ Keyword hits: up to 50 points', fontsize=8)
ax2.text(7, 3.2, '- Short submission penalty', fontsize=8)
ax2.text(7, 2.9, 'Feedback: strengths + improvements + next_step', fontsize=8, style='italic')

# ============= FLOW 3: Knowledge Extraction =============
ax3 = axes[2]
setup_ax(ax3, '3. Knowledge Extraction Flow')

draw_box(ax3, 0.3, 1.5, 2, 2, 'Raw Text\n(STT/Slack)', colors['user'], colors['user_border'])
draw_box(ax3, 3.5, 1.5, 2.5, 2, 'Ingestion\nModule', colors['process'], colors['process_border'])
draw_box(ax3, 7, 1.5, 2.5, 2, 'Extractor\nCapability', colors['llm'], colors['llm_border'])
draw_box(ax3, 10.5, 2.5, 3, 1.5, 'Tag\nDetection', colors['data'], colors['data_border'])
draw_box(ax3, 10.5, 0.5, 3, 1.5, 'Sentence\nSplit', colors['data'], colors['data_border'])
draw_box(ax3, 14, 1.5, 1.5, 2, 'Knowledge\nItems', colors['result'], colors['result_border'])

draw_arrow(ax3, (2.3, 2.5), (3.5, 2.5))
draw_arrow(ax3, (6, 2.5), (7, 2.5), 'extract()')
draw_arrow(ax3, (9.5, 2.8), (10.5, 3.25))
draw_arrow(ax3, (9.5, 2.2), (10.5, 1.25))
draw_arrow(ax3, (13.5, 3.25), (14, 2.8))
draw_arrow(ax3, (13.5, 1.25), (14, 2.2))

# Tag types
ax3.text(7, 4.2, 'Knowledge Tags:', fontsize=9, fontweight='bold')
ax3.text(7, 3.8, 'RULE: rules, principles, must/never', fontsize=8)
ax3.text(7, 3.5, 'PITFALL: caution, mistakes, traps', fontsize=8)
ax3.text(7, 3.2, 'GLOSSARY: definitions, terms', fontsize=8)
ax3.text(7, 2.9, 'PROCESS: procedures, workflows', fontsize=8, style='italic')

plt.tight_layout()
plt.savefig('docs/data_flow_v1.2.png', dpi=150, bbox_inches='tight',
            facecolor='#FAFAFA', edgecolor='none')
print("Data flow diagram saved to docs/data_flow_v1.2.png")

"""GIF 动画生成公共库（生成后删除）
统一风格：上方代码 + 黄色高亮当前行，下方动画，指针用彩色圆角框表示。
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation

# ---------- 配色 ----------
YELLOW = '#ffeb3b'
YELLOW_EDGE = '#fbc02d'
CODE_BG = '#f8f9fa'
ANIM_BG = '#fafafa'
CELL_BG = '#f9f9f9'
CELL_EDGE = '#aaaaaa'
PTR = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6',
       '#e67e22', '#1abc9c', '#e91e63', '#795548',
       '#34495e', '#f1c40f']


def _draw_code(ax, lines, cur, line_gap=1.8, fontsize=11):
    ax.clear()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, len(lines) * line_gap + 0.8)
    ax.axis('off')
    for i, txt in enumerate(lines):
        y = (len(lines) - i - 0.5) * line_gap
        bbox = None
        fw = 'normal'
        if i + 1 == cur:
            bbox = dict(boxstyle='round,pad=0.02', facecolor=YELLOW,
                        edgecolor=YELLOW_EDGE, linewidth=1.5)
            fw = 'bold'
        ax.text(0.05, y, txt, va='center', fontsize=fontsize,
                family='monospace', bbox=bbox, fontweight=fw)


def render(filename, code_lines, frames, draw_state, interval=700, hold=5,
           figsize=(12, 9), ratio=(1.5, 2.2), dpi=110):
    """frames: [(code_line_no, state), ...]; draw_state(ax, state) 绘制动画区。"""
    fig, (axc, axa) = plt.subplots(
        2, 1, figsize=figsize, gridspec_kw={'height_ratios': list(ratio)})
    axc.set_facecolor(CODE_BG)
    axa.set_facecolor(ANIM_BG)

    def tick(fr):
        line, state = fr
        _draw_code(axc, code_lines, line)
        axa.clear()
        axa.axis('off')
        draw_state(axa, state)

    seq = list(frames) + [frames[-1]] * hold
    ani = FuncAnimation(fig, tick, frames=seq, repeat=True, interval=interval)
    ani.save(filename, writer='pillow', fps=max(1, 1000 // interval), dpi=dpi)
    plt.close(fig)
    print('saved', filename)


# ---------- 基础绘制 ----------
def cell(ax, x, y, w, h, text, fc=CELL_BG, ec=CELL_EDGE, lw=1.2,
         fs=13, weight='bold', tc='black', alpha=1.0):
    ax.add_patch(patches.Rectangle((x, y), w, h, linewidth=lw,
                                   edgecolor=ec, facecolor=fc, alpha=alpha))
    ax.text(x + w / 2, y + h / 2, str(text), ha='center', va='center',
            fontsize=fs, fontweight=weight, color=tc, alpha=alpha)


def ptrbox(ax, x, y, w, h, color, lw=3.5, pad=0.03, alpha=0.95):
    ax.add_patch(patches.FancyBboxPatch(
        (x, y), w, h, boxstyle=f'round,pad={pad}', linewidth=lw,
        edgecolor=color, facecolor='none', alpha=alpha))


def label(ax, x, y, text, color='black', fs=10, weight='bold',
          ha='center', va='center'):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs, color=color,
            fontweight=weight)


def arrow(ax, x1, y1, x2, y2, color='#555555', lw=1.5, style='-|>'):
    ax.add_patch(patches.FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle=style, mutation_scale=12,
        color=color, lw=lw, shrinkA=0, shrinkB=0))


def rect(ax, x, y, w, h, fc='none', ec=CELL_EDGE, lw=1.2, alpha=1.0):
    ax.add_patch(patches.Rectangle((x, y), w, h, linewidth=lw,
                                   edgecolor=ec, facecolor=fc, alpha=alpha))


def circle_node(ax, x, y, text, r=0.32, fc='#ffffff', ec='#444444',
                fs=11, lw=2):
    ax.add_patch(patches.Circle((x, y), r, facecolor=fc, edgecolor=ec,
                                linewidth=lw, zorder=2))
    ax.text(x, y, str(text), ha='center', va='center', fontsize=fs,
            fontweight='bold', zorder=3)


def line(ax, x1, y1, x2, y2, color='#777777', lw=1.5, ls='-'):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, ls=ls, zorder=0)


def canvas(ax, xlim, ylim, equal=True):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    if equal:
        ax.set_aspect('equal')

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
from gif_common import (render, cell, ptrbox, label, canvas, line,
                        circle_node, PTR, YELLOW_EDGE)

RB_CODE = [
    "void insert_fixup(Node** root, Node* z) {",
    "    while (z != *root && z->parent->color == RED) {",
    "        Node* y = uncle(z);",
    "        if (y != NULL && y->color == RED) {",
    "            z->parent->color = BLACK;",
    "            y->color = BLACK;",
    "            z->parent->parent->color = RED;",
    "            z = z->parent->parent;",
    "        } else {",
    "            if (z == z->parent->right) {",
    "                z = z->parent;",
    "                rotate_left(root, z);",
    "            }",
    "            z->parent->color = BLACK;",
    "            z->parent->parent->color = RED;",
    "            rotate_right(root, z->parent->parent);",
    "        }",
    "    }",
    "    (*root)->color = BLACK;",
    "}",
]

XORD = {5: 0.9, 10: 2.8, 15: 4.7, 20: 6.6, 25: 8.5, 27: 10.4, 30: 12.3}
TOP = 7.7
DY = 1.45
R = 0.5
REDF = '#e74c3c'
BLKF = '#2c3e50'
NULLX, NULLY = 13.45, 4.8


def clone(T):
    return {k: list(v) for k, v in T.items()}


def ring(ax, x, y, color, lw, d=0.1):
    ax.add_patch(mpatches.Circle((x, y), R + d, facecolor='none',
                                 edgecolor=color, linewidth=lw, zorder=5))


def rot_arc(ax, p1, p2, rad=0.45, color='#f39c12'):
    ax.add_patch(mpatches.FancyArrowPatch(
        p1, p2, connectionstyle='arc3,rad=%.2f' % rad,
        arrowstyle='-|>', mutation_scale=18, color=color, lw=3,
        shrinkA=20, shrinkB=20, zorder=1))


def draw_rb(ax, s):
    canvas(ax, (0, 14), (2.6, 8.7))
    T, root = s['T'], s['root']
    z, y, flash = s.get('z'), s.get('y'), s.get('flash')
    ov = s.get('pos') or {}
    hl = s.get('hl_edges') or []
    dep = {}
    todo = [(root, 0)]
    while todo:
        v, d = todo.pop()
        dep[v] = d
        l, r = T[v][1], T[v][2]
        if l is not None:
            todo.append((l, d + 1))
        if r is not None:
            todo.append((r, d + 1))

    def P(v):
        return ov.get(v) or (XORD[v], TOP - dep[v] * DY)

    for v in T:
        for ch in (T[v][1], T[v][2]):
            if ch is not None:
                line(ax, P(v)[0], P(v)[1], P(ch)[0], P(ch)[1])
    for a, b in hl:
        line(ax, P(a)[0], P(a)[1], P(b)[0], P(b)[1], color='#f39c12', lw=3.4)
    if s.get('arc'):
        a, b = s['arc']
        rot_arc(ax, P(a), P(b))
    if s.get('ynull'):
        ax.add_patch(mpatches.FancyBboxPatch(
            (NULLX - 0.62, NULLY - 0.32), 1.24, 0.64,
            boxstyle='round,pad=0.05', linewidth=2.2, edgecolor=PTR[3],
            facecolor='none', linestyle='--', zorder=3))
        ax.text(NULLX, NULLY, 'NULL', ha='center', va='center', fontsize=10,
                color='#666666', fontweight='bold', zorder=4)
    for v in T:
        col = T[v][0]
        x, yv = P(v)
        ax.add_patch(mpatches.Circle((x, yv), R,
                                     facecolor=REDF if col == 'R' else BLKF,
                                     edgecolor='#2b2b2b', linewidth=1.5,
                                     zorder=2))
        ax.text(x, yv, str(v), ha='center', va='center', fontsize=12,
                fontweight='bold', color='white', zorder=4)
        if v == z:
            ring(ax, x, yv, PTR[1], 3.6)
            label(ax, x - R - 0.34, yv - R - 0.1, 'z', color=PTR[1], fs=13)
        if v == y:
            ring(ax, x, yv, PTR[3], 3.2)
            label(ax, x + R + 0.34, yv + R + 0.12, 'y', color=PTR[3], fs=13)
        if v == flash:
            ring(ax, x, yv, YELLOW_EDGE, 4.2, d=0.16)


def gen_rb(path):
    T0 = {20: ['B', 10, 30], 10: ['R', 5, 15], 30: ['B', 25, None],
          5: ['B', None, None], 15: ['B', None, None], 25: ['R', None, None]}
    T1 = clone(T0)
    T1[25][2] = 27
    T1[27] = ['R', None, None]
    T2 = clone(T1)
    T2[30][1] = 27
    T2[27] = ['R', 25, None]
    T2[25] = ['R', None, None]
    T3 = clone(T2)
    T3[27][0] = 'B'
    T4 = clone(T3)
    T4[30][0] = 'R'
    T5 = clone(T4)
    T5[20][2] = 27
    T5[27] = ['B', 25, 30]
    T5[30] = ['R', None, None]

    YN = dict(ynull=True)
    fr = [
        (1, dict(T=clone(T0), root=20)),
        (1, dict(T=clone(T1), root=20, z=27)),
        (2, dict(T=clone(T1), root=20, z=27)),
        (3, dict(T=clone(T1), root=20, z=27, **YN)),
        (4, dict(T=clone(T1), root=20, z=27, **YN)),
        (9, dict(T=clone(T1), root=20, z=27)),
        (10, dict(T=clone(T1), root=20, z=27, arc=(25, 27))),
        (11, dict(T=clone(T1), root=20, z=25)),
        (12, dict(T=clone(T1), root=20, z=25, arc=(25, 27),
                  hl_edges=[(30, 25), (25, 27)])),
        (12, dict(T=clone(T2), root=20, z=25, pos={25: (8.5, 4.075),
                                                   27: (10.4, 4.075)},
                  hl_edges=[(30, 27), (27, 25)])),
        (12, dict(T=clone(T2), root=20, z=25,
                  hl_edges=[(30, 27), (27, 25)])),
        (14, dict(T=clone(T3), root=20, z=25, flash=27)),
        (15, dict(T=clone(T4), root=20, z=25, flash=30)),
        (16, dict(T=clone(T4), root=20, z=25, arc=(30, 27),
                  hl_edges=[(20, 30), (30, 27)])),
        (16, dict(T=clone(T5), root=20, z=25, pos={27: (10.4, 5.525),
                                                   30: (12.3, 5.525)},
                  hl_edges=[(20, 27), (27, 30)])),
        (16, dict(T=clone(T5), root=20, z=25,
                  hl_edges=[(20, 27), (27, 30)])),
        (2, dict(T=clone(T5), root=20, z=25)),
        (19, dict(T=clone(T5), root=20, flash=20)),
        (20, dict(T=clone(T5), root=20)),
    ]
    render(path, RB_CODE, fr, draw_rb, ratio=(1.9, 2.3))


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen_rb(os.path.join(d, 'rb_insert_fix.gif'))

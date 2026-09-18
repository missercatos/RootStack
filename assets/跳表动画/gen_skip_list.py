import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
from gif_common import render, cell, ptrbox, label, canvas, line, PTR

X0 = 2.6
DX = 1.4
NW, NH = 1.0, 0.85
ROWS = {0: [1, 2, 3, 4, 5, 6, 7, 8],
        1: [1, 3, 5, 7],
        2: [1, 5]}
RY = {0: 2.1, 1: 4.0, 2: 5.9}
HX, HW = 0.5, 0.9
NULLX, NULLW = 13.1, 0.8

CODE = [
    "Node* search(Node* head, int key) {",
    "    Node* p = head;",
    "    for (int i = level - 1; i >= 0; i--) {",
    "        while (p->next[i] != NULL &&",
    "               p->next[i]->key < key) {",
    "            p = p->next[i];",
    "        }",
    "    }",
    "    p = p->next[0];",
    "    return p;",
    "}",
]


def col(k):
    return X0 + (k - 1) * DX


def box_xy(k, lv):
    return col(k) - NW / 2, RY[lv] - NH / 2


def edge(ax, x1, y1, x2, y2, color='#666666', lw=1.6, z=1):
    ax.add_patch(mpatches.FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=12,
        color=color, lw=lw, shrinkA=0, shrinkB=1, zorder=z))


def draw_skip(ax, s):
    canvas(ax, (0, 14), (0.9, 7.35))
    p, lvl, chk, found = s.get('p'), s.get('i'), s.get('chk'), s.get('found')
    for k in ROWS[0]:
        lvs = [lv for lv in ROWS if k in ROWS[lv]]
        line(ax, col(k), RY[min(lvs)], col(k), RY[max(lvs)],
             color='#d9d9d9', lw=1.2, ls=(0, (2, 2)))
    for lv in ROWS:
        y = RY[lv]
        seq = ['H'] + ROWS[lv]
        for a, b in zip(seq, seq[1:]):
            x1 = HX + HW if a == 'H' else col(a) + NW / 2
            edge(ax, x1, y, col(b) - NW / 2, y)
        edge(ax, col(ROWS[lv][-1]) + NW / 2, y, NULLX, y)
        label(ax, 0.28, y, str(lv), color='#999999', fs=10)
    cell(ax, HX, RY[0] - 0.5, HW, RY[2] - RY[0] + 1.0, 'head', fc='#ffffff',
         ec='#444444', fs=11)
    for lv in ROWS:
        cell(ax, NULLX, RY[lv] - 0.3, NULLW, 0.6, 'NULL', fc='#f2f2f2',
             ec='#bbbbbb', fs=9)
    for lv in ROWS:
        for k in ROWS[lv]:
            x, y = box_xy(k, lv)
            fc, ec = '#ffffff', '#444444'
            if found and k == 7:
                fc, ec = '#d5f5e3', PTR[2]
            cell(ax, x, y, NW, NH, k, fc=fc, ec=ec, fs=13)
    if chk:
        lv, nxt = chk
        y = RY[lv]
        x1 = HX + HW if p == 'H' else col(p) + NW / 2
        x2 = NULLX if nxt is None else col(nxt) - NW / 2
        edge(ax, x1, y, x2, y, color=PTR[4], lw=2.8, z=4)
    if p == 'H':
        ptrbox(ax, HX, RY[0] - 0.5, HW, RY[2] - RY[0] + 1.0, PTR[0],
               lw=3.2, pad=0.02)
    elif p is not None:
        lv = lvl if lvl in ROWS else 0
        if p in ROWS[lv]:
            x, y = box_xy(p, lv)
            ptrbox(ax, x, y, NW, NH, PTR[0], lw=3.2, pad=0.02)
    if lvl is not None:
        cell(ax, 0.45, 6.55, 1.9, 0.68, 'i = %d' % lvl, fc='#eaf2fb',
             ec='#bbbbbb', fs=11)
        ptrbox(ax, 0.45, 6.55, 1.9, 0.68, PTR[1], lw=2.6, pad=0.02)
    cell(ax, 2.65, 6.55, 2.8, 0.68, 'key = 7', fc='#f6eafb',
         ec='#bbbbbb', fs=11)
    ptrbox(ax, 2.65, 6.55, 2.8, 0.68, PTR[3], lw=2.6, pad=0.02)


def snap(**kw):
    d = dict(p=None, i=None, chk=None, found=False)
    d.update(kw)
    return d


def gen(path):
    f = []
    f.append((1, snap()))
    f.append((2, snap(p='H')))
    f.append((3, snap(p='H', i=2)))
    f.append((4, snap(p='H', i=2, chk=(2, 1))))
    f.append((5, snap(p='H', i=2, chk=(2, 1))))
    f.append((6, snap(p=1, i=2)))
    f.append((4, snap(p=1, i=2, chk=(2, 5))))
    f.append((5, snap(p=1, i=2, chk=(2, 5))))
    f.append((6, snap(p=5, i=2)))
    f.append((4, snap(p=5, i=2, chk=(2, None))))
    f.append((3, snap(p=5, i=1)))
    f.append((5, snap(p=5, i=1, chk=(1, 7))))
    f.append((3, snap(p=5, i=0)))
    f.append((5, snap(p=5, i=0, chk=(0, 6))))
    f.append((6, snap(p=6, i=0)))
    f.append((5, snap(p=6, i=0, chk=(0, 7))))
    f.append((8, snap(p=6)))
    f.append((9, snap(p=7, found=True)))
    f.append((10, snap(p=7, found=True)))
    f.append((11, snap(p=7, found=True)))
    render(path, CODE, f, draw_skip, interval=750)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen(os.path.join(d, 'skip_search.gif'))

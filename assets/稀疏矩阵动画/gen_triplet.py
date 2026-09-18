import os
import matplotlib
matplotlib.use('Agg')
from gif_common import render, cell, ptrbox, label, canvas, arrow, PTR

CODE = [
    "void transpose(Triplet* a, Triplet* b) {",
    "    b->rows = a->cols;",
    "    b->cols = a->rows;",
    "    b->nums = a->nums;",
    "    if (b->nums == 0) return;",
    "    int q = 0;",
    "    for (int col = 0; col < a->cols; col++) {",
    "        for (int p = 0; p < a->nums; p++) {",
    "            if (a->data[p].col == col) {",
    "                b->data[q].row = a->data[p].col;",
    "                b->data[q].col = a->data[p].row;",
    "                b->data[q].val = a->data[p].val;",
    "                q++;",
    "            }",
    "        }",
    "    }",
    "}",
]

COLW, CELLH, ROWH = 1.45, 0.58, 0.62
AX, BX = 1.2, 8.45
META_Y, HDR_Y, DATA_Y0 = 5.05, 4.35, 3.67
A_ROWS = [[0, 0, 1], [0, 2, 2], [1, 1, 3], [2, 0, 4], [2, 2, 5]]
META_LBL = ['rows', 'cols', 'nums']


def draw_table(ax, x0, meta, data, hl_row=None, row_color=PTR[1],
               hl_cell=None, cell_color=PTR[4], meta_done=False):
    for j, v in enumerate(meta):
        fc = '#eaf7ee' if meta_done and v is not None else '#eef2f6'
        cell(ax, x0 + j * COLW, META_Y, COLW, 0.62,
             '' if v is None else v, fc=fc, fs=14)
        label(ax, x0 + j * COLW + COLW / 2, META_Y + 0.78, META_LBL[j],
              color='#999999', fs=9)
    for j, t in enumerate(('row', 'col', 'val')):
        cell(ax, x0 + j * COLW, HDR_Y, COLW, CELLH, t, fc='#f7f9fb',
             ec='#cccccc', fs=11, tc='#888888')
    for r in range(5):
        y = DATA_Y0 - r * ROWH
        vals = data[r] if r < len(data) else (None, None, None)
        for c in range(3):
            fc = '#ffffff'
            if hl_cell == (r, c):
                fc = cell_color
            cell(ax, x0 + c * COLW, y, COLW, CELLH,
                 '' if vals[c] is None else vals[c], fc=fc, fs=13)
        if hl_row == r:
            ptrbox(ax, x0 - 0.05, y - 0.03, 3 * COLW + 0.1, CELLH + 0.06,
                   row_color, lw=2.6)


def draw(ax, s):
    canvas(ax, (0, 14), (0, 6))
    p = s.get('p')
    draw_table(ax, AX, [3, 3, 5], A_ROWS, hl_row=p, row_color=PTR[1],
               hl_cell=(p, 1) if p is not None else None,
               cell_color=PTR[2] if s.get('match') else PTR[4])
    draw_table(ax, BX, s['bmeta'], s['b'], hl_row=s.get('brow'),
               row_color=PTR[2], meta_done=True)
    if s.get('writing'):
        y1 = DATA_Y0 - s['p'] * ROWH + CELLH / 2
        y2 = DATA_Y0 - s['brow'] * ROWH + CELLH / 2
        arrow(ax, AX + 3 * COLW + 0.18, y1, BX - 0.18, y2,
              color=PTR[2], lw=1.8)
    vx = 4.8
    for name, color, val in (('col', PTR[4], s.get('col')),
                             ('p', PTR[1], s.get('p')),
                             ('q', PTR[2], s.get('q'))):
        cell(ax, vx, 0.4, 1.3, 0.62, '' if val is None else val,
             fc='#ffffff', ec=color, lw=2, fs=14)
        ptrbox(ax, vx, 0.4, 1.3, 0.62, color, lw=2.4)
        label(ax, vx + 0.65, 0.16, name, color=color, fs=11)
        vx += 1.55


def gen(path):
    b = [[None, None, None] for _ in range(5)]
    bmeta = [None, None, None]
    frames = []

    def st(**kw):
        d = dict(b=[list(r) for r in b], bmeta=list(bmeta))
        d.update(kw)
        return d

    frames.append((1, st()))
    bmeta[0] = 3
    frames.append((2, st()))
    bmeta[1] = 3
    frames.append((3, st()))
    bmeta[2] = 5
    frames.append((4, st()))
    frames.append((5, st()))
    q = 0
    frames.append((6, st(q=q)))
    for col in range(3):
        frames.append((7, st(col=col, q=q)))
        for p in range(5):
            frames.append((8, st(col=col, p=p, q=q)))
            if A_ROWS[p][1] == col:
                frames.append((9, st(col=col, p=p, q=q, match=True)))
                b[q] = [A_ROWS[p][1], None, None]
                frames.append((10, st(col=col, p=p, q=q, match=True,
                                       brow=q, writing=True)))
                b[q][1] = A_ROWS[p][0]
                frames.append((11, st(col=col, p=p, q=q, match=True,
                                       brow=q, writing=True)))
                b[q][2] = A_ROWS[p][2]
                frames.append((12, st(col=col, p=p, q=q, match=True,
                                       brow=q, writing=True)))
                q += 1
                frames.append((13, st(col=col, p=p, q=q, brow=q - 1)))
    frames.append((17, st()))
    render(path, CODE, frames, draw)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen(os.path.join(d, 'triplet_transpose.gif'))

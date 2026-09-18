import os
import matplotlib
matplotlib.use('Agg')
from gif_common import (render, cell, ptrbox, canvas, rect, PTR)

BLOCK_SEARCH_CODE = [
    "#define BS 3",
    "int block_search(Index* idx, int* a, int n, int key) {",
    "    int b = -1;",
    "    for (int i = 0; i < idx->blocks; i++) {",
    "        if (key <= idx->max[i]) {",
    "            b = i;",
    "            break;",
    "        }",
    "    }",
    "    if (b == -1) return -1;",
    "    for (int i = b * BS; i < (b + 1) * BS && i < n; i++) {",
    "        if (a[i] == key) return i;",
    "        if (a[i] > key) break;",
    "    }",
    "    return -1;",
    "}",
]

ARR = [8, 12, 15, 18, 23, 27, 32, 36, 41, 45, 49, 52]
IMAX = [15, 27, 41, 52]
BS = 3
KEY = 23
BLK = ['#e3f2fd', '#e8f5e9', '#fff3e0', '#f3e5f5']
HIT_FC = '#a5d6a7'
EXAM_FC = '#fff8e1'
CUR_I = PTR[3]
SEL_B = PTR[1]
KEY_C = PTR[0]
AW, AH, AX0, AY = 0.92, 0.95, 0.4, 2.35
IH, IY = 0.95, 4.45


def draw_search(ax, s):
    canvas(ax, (0.1, 11.8), (0.0, 6.8))
    cell(ax, 0.4, 5.62, 2.35, 0.85, "key = %d" % KEY, fc='#ffffff',
         ec=KEY_C, lw=2, fs=13)
    ptrbox(ax, 0.4, 5.62, 2.35, 0.85, KEY_C, lw=2.5)
    for b in range(4):
        cell(ax, AX0 + b * BS * AW, IY, BS * AW, IH, IMAX[b], fc=BLK[b],
             fs=15, ec='#666666')
    cur = s.get('cursor')
    if cur and cur[0] == 'idx':
        b = cur[1]
        ptrbox(ax, AX0 + b * BS * AW, IY, BS * AW, IH, CUR_I)
    if s.get('b') is not None:
        b = s['b']
        ptrbox(ax, AX0 + b * BS * AW, IY, BS * AW, IH, SEL_B, lw=4)
    for i, v in enumerate(ARR):
        b = i // BS
        fc = BLK[b]
        if s.get('exam') == i:
            fc = EXAM_FC
        if s.get('hit') == i:
            fc = HIT_FC
        cell(ax, AX0 + i * AW, AY, AW, AH, v, fc=fc, fs=13)
    if cur and cur[0] == 'arr':
        ptrbox(ax, AX0 + cur[1] * AW, AY, AW, AH, CUR_I)
    if s.get('hit') is not None:
        ptrbox(ax, AX0 + s['hit'] * AW, AY, AW, AH, '#2ecc71', lw=4)
    for b in range(1, 4):
        line_x = AX0 + b * BS * AW
        rect(ax, line_x - 0.02, AY - 0.12, 0.04, AH + 0.24, fc='#888888',
             ec='#888888')


def block_frames():
    fr = []

    def snap(ln, **kw):
        fr.append((ln, dict(**kw)))

    snap(2, b=None, cursor=None)
    snap(3, b=None, cursor=None)
    b = None
    for i in range(4):
        snap(4, b=b, cursor=('idx', i))
        ok = KEY <= IMAX[i]
        snap(5, b=b, cursor=('idx', i), exam=None, valid=ok)
        if ok:
            b = i
            snap(6, b=b, cursor=('idx', i))
            snap(7, b=b, cursor=('idx', i), sel=b)
            break
    snap(10, b=b, cursor=None, sel=b)
    for i in range(b * BS, min((b + 1) * BS, len(ARR))):
        snap(11, b=b, cursor=('arr', i), sel=b)
        if ARR[i] == KEY:
            snap(12, b=b, cursor=None, sel=b, hit=i, exam=i)
            snap(16, b=b, cursor=None, sel=b, hit=i)
            return fr
        snap(12, b=b, cursor=('arr', i), sel=b, exam=i)
        if ARR[i] > KEY:
            snap(13, b=b, cursor=('arr', i), sel=b, exam=i)
            break
        snap(13, b=b, cursor=('arr', i), sel=b, exam=i)
    snap(15, b=b, cursor=None, sel=b)
    return fr


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    render(os.path.join(d, 'block_search.gif'), BLOCK_SEARCH_CODE,
           block_frames(), draw_search)

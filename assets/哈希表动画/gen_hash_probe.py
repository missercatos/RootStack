import os
import matplotlib
matplotlib.use('Agg')
from gif_common import render, cell, ptrbox, label, canvas, PTR

CODE = [
    "int insert(int* t, int key) {",
    "    int i = key % M;",
    "    while (t[i] != -1) {",
    "        i = (i + 1) % M;",
    "    }",
    "    t[i] = key;",
    "    return i;",
    "}",
]

M = 7
TX0, TY, TW, TH = 1.6, 2.5, 1.5, 0.95
KEYS = [5, 12, 19, 26, 33]


def draw(ax, s):
    canvas(ax, (0, 14), (0, 6))
    key = s['key']
    cell(ax, 1.6, 4.4, 1.5, 0.8, key, fc='#ffffff', ec=PTR[1], lw=2, fs=15)
    ptrbox(ax, 1.6, 4.4, 1.5, 0.8, PTR[1], lw=2.6)
    label(ax, 2.35, 5.4, 'key', color=PTR[1], fs=12)
    i = s.get('i')
    cell(ax, 3.4, 4.4, 1.3, 0.8, '' if i is None else i, fc='#ffffff',
         ec=PTR[4], lw=2, fs=15)
    ptrbox(ax, 3.4, 4.4, 1.3, 0.8, PTR[4], lw=2.6)
    label(ax, 4.05, 5.4, 'i', color=PTR[4], fs=12)

    vals = s['vals']
    chk = s.get('check')
    plc = s.get('placed')
    for k in range(M):
        x = TX0 + k * TW
        fc = '#f9f9f9'
        if chk == k:
            fc = '#e8f5e9' if vals[k] is None else '#ffebee'
        if plc == k:
            fc = '#e8f5e9'
        cell(ax, x, TY, TW, TH, vals[k] if vals[k] is not None else -1,
             fc=fc, fs=15)
        label(ax, x + TW / 2, TY - 0.25, str(k), color='#999999', fs=10)
    if chk is not None:
        ptrbox(ax, TX0 + chk * TW, TY, TW, TH, PTR[4], lw=3)
        label(ax, TX0 + chk * TW + TW / 2, TY + TH + 0.3, 'i',
              color=PTR[4], fs=12)
    if plc is not None:
        ptrbox(ax, TX0 + plc * TW, TY, TW, TH, PTR[2], lw=3)
        label(ax, TX0 + plc * TW + TW / 2, TY + TH + 0.3, 't[i]',
              color=PTR[2], fs=12)


def st(vals, key, i=None, check=None, placed=None):
    return dict(vals=list(vals), key=key, i=i, check=check, placed=placed)


def gen(path):
    vals = [None] * M
    frames = []
    for key in KEYS:
        frames.append((1, st(vals, key)))
        i = key % M
        frames.append((2, st(vals, key, i=i)))
        while vals[i] is not None:
            frames.append((3, st(vals, key, i=i, check=i)))
            i = (i + 1) % M
            frames.append((4, st(vals, key, i=i)))
        frames.append((3, st(vals, key, i=i, check=i)))
        vals = list(vals)
        vals[i] = key
        frames.append((5, st(vals, key, i=i, placed=i)))
        frames.append((6, st(vals, key, i=i, placed=i)))
    render(path, CODE, frames, draw)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen(os.path.join(d, 'hash_probing.gif'))

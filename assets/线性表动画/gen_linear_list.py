import os
import matplotlib
matplotlib.use('Agg')
from gif_common import render, cell, ptrbox, label, canvas, PTR

W, H = 1.0, 0.8
NCELL = 8
BASE_Y = 1.0


def draw_array(ax, vals, src=None, dst=None, moved=None):
    canvas(ax, (-0.6, NCELL * W + 0.6), (-0.9, 2.3))
    for k in range(NCELL):
        v = vals[k] if k < len(vals) and vals[k] is not None else ''
        fc = '#fff8e1' if k == moved else '#f9f9f9'
        cell(ax, k * W, BASE_Y, W, H, v, fc=fc, fs=14)
        label(ax, k * W + W / 2, BASE_Y - 0.35, str(k), color='#999999', fs=9)
    if src is not None:
        ptrbox(ax, src * W, BASE_Y, W, H, PTR[0])
    if dst is not None:
        ptrbox(ax, dst * W, BASE_Y, W, H, PTR[1])


INSERT_CODE = [
    "int list_insert(int* a, int n, int i, int x) {",
    "    for (int j = n; j > i; j--) {",
    "        a[j] = a[j - 1];",
    "    }",
    "    a[i] = x;",
    "    return n + 1;",
    "}",
]

DELETE_CODE = [
    "int list_delete(int* a, int n, int i) {",
    "    int x = a[i];",
    "    for (int j = i; j < n - 1; j++) {",
    "        a[j] = a[j + 1];",
    "    }",
    "    return n - 1;",
    "}",
]


def gen_insert(path):
    vals = [10, 20, 30, 40, 50, None, None, None]
    n, i, x = 5, 2, 99
    frames = [(1, dict(vals=list(vals)))]
    cur = list(vals)
    for j in range(n, i, -1):
        src = j - 1
        dst = j
        cur = list(cur)
        cur[dst] = cur[src]
        frames.append((3, dict(vals=list(cur), src=src, dst=dst, moved=dst)))
    cur[i] = x
    frames.append((5, dict(vals=list(cur), dst=i, moved=i)))
    frames.append((6, dict(vals=list(cur))))
    render(path, INSERT_CODE, frames,
           lambda ax, s: draw_array(ax, s['vals'], s.get('src'), s.get('dst'), s.get('moved')))


def gen_delete(path):
    vals = [10, 20, 30, 40, 50, None, None, None]
    n, i = 5, 2
    frames = [(2, dict(vals=list(vals), dst=i, moved=i))]
    cur = list(vals)
    for j in range(i, n - 1):
        src = j + 1
        dst = j
        cur = list(cur)
        cur[dst] = cur[src]
        cur[src] = None
        frames.append((4, dict(vals=list(cur), src=src, dst=dst, moved=dst)))
    frames.append((6, dict(vals=list(cur))))
    render(path, DELETE_CODE, frames,
           lambda ax, s: draw_array(ax, s['vals'], s.get('src'), s.get('dst'), s.get('moved')))


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen_insert(os.path.join(d, 'seq_insert.gif'))
    gen_delete(os.path.join(d, 'seq_delete.gif'))

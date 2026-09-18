import os
import matplotlib
matplotlib.use('Agg')
from gif_common import render, cell, ptrbox, label, canvas, line, arrow, circle_node, PTR

CELL_W = 1.4
CELL_H = 1.0
ARR_Y = 1.0
TX0 = 1.4
SPAN = 11.2
Y0 = 7.3
DY = 1.25
R = 0.45

SIFT_DOWN = [
    "void sift_down(int* a, int n, int i) {",
    "    while (2 * i + 1 < n) {",
    "        int c = 2 * i + 1;",
    "        if (c + 1 < n && a[c + 1] > a[c]) c++;",
    "        if (a[i] >= a[c]) break;",
    "        int t = a[i];",
    "        a[i] = a[c];",
    "        a[c] = t;",
    "        i = c;",
    "    }",
    "}",
]

SIFT_UP = [
    "void sift_up(int* a, int i) {",
    "    while (i > 0) {",
    "        int p = (i - 1) / 2;",
    "        if (a[p] >= a[i]) break;",
    "        int t = a[p];",
    "        a[p] = a[i];",
    "        a[i] = t;",
    "        i = p;",
    "    }",
    "}",
]


def dep(k):
    return (k + 1).bit_length() - 1


def nx(k):
    d = dep(k)
    pos = k - (2 ** d - 1)
    return TX0 + (pos + 0.5) * (SPAN / (2 ** d))


def ny(k):
    return Y0 - dep(k) * DY


def link(ax, k1, k2, color='#c0392b', style='<|-|>'):
    x1, y1 = nx(k1), ny(k1)
    x2, y2 = nx(k2), ny(k2)
    dx, dy = x2 - x1, y2 - y1
    d = max((dx * dx + dy * dy) ** 0.5, 1e-9)
    ux, uy = dx / d, dy / d
    arrow(ax, x1 + ux * (R + 0.06), y1 + uy * (R + 0.06),
          x2 - ux * (R + 0.06), y2 - uy * (R + 0.06), color=color,
          lw=1.6, style=style)


def draw_heap(ax, s):
    vals = s['vals']
    n = s['n']
    canvas(ax, (0, 14), (0.3, 8.2))
    for k in range(1, n):
        p = (k - 1) // 2
        line(ax, nx(p), ny(p), nx(k), ny(k))
    for k in range(n):
        cell(ax, TX0 + k * CELL_W, ARR_Y, CELL_W, CELL_H, vals[k], fs=15)
        label(ax, TX0 + k * CELL_W + CELL_W / 2, ARR_Y - 0.4,
              str(k), color='#999999', fs=9)
    i, c, p, new = s.get('i'), s.get('c'), s.get('p'), s.get('new')
    swp = s.get('swp')
    for k in range(n):
        x, y = nx(k), ny(k)
        fc = '#ffffff'
        ec, lw = '#444444', 2
        if swp and k in swp:
            fc = '#fff3cd'
        if k == new:
            fc = '#e8f5e9'
        if k == i:
            ec, lw = PTR[0], 3.6
        elif k == c:
            ec, lw = PTR[1], 3.6
        elif k == p:
            ec, lw = PTR[3], 3.0
        circle_node(ax, x, y, vals[k], r=R, fc=fc, ec=ec, fs=12, lw=lw)
        label(ax, x, y - R - 0.28, str(k), color='#999999', fs=9)
    if swp:
        cell(ax, TX0 + swp[0] * CELL_W, ARR_Y, CELL_W, CELL_H, vals[swp[0]],
             fc='#fff3cd', fs=15)
        cell(ax, TX0 + swp[1] * CELL_W, ARR_Y, CELL_W, CELL_H, vals[swp[1]],
             fc='#fff3cd', fs=15)
        link(ax, swp[0], swp[1])
    cmpk = s.get('cmp')
    if cmpk:
        link(ax, cmpk[0], cmpk[1], color='#e67e22', style='-')
    if i is not None:
        label(ax, nx(i) - R - 0.25, ny(i) + R + 0.15, 'i', color=PTR[0], fs=12)
    if c is not None:
        label(ax, nx(c) + R + 0.25, ny(c) + R + 0.15, 'c', color=PTR[1], fs=12)
    if s.get('p') is not None:
        label(ax, nx(s['p']) - R - 0.25, ny(s['p']) + R + 0.15, 'p',
              color=PTR[3], fs=12)


def gen_siftdown(path):
    a = [1, 5, 3, 8, 2]
    n = len(a)
    fr = [(1, dict(vals=list(a), n=n, i=0))]
    i = 0
    while 2 * i + 1 < n:
        st = dict(vals=list(a), n=n, i=i)
        fr.append((2, dict(st)))
        c = 2 * i + 1
        fr.append((3, dict(st, c=c)))
        fr.append((4, dict(st, c=c, cmp=(c, c + 1))))
        if c + 1 < n and a[c + 1] > a[c]:
            c += 1
        fr.append((5, dict(st, c=c, cmp=(i, c))))
        if a[i] >= a[c]:
            break
        fr.append((6, dict(vals=list(a), n=n, i=i, c=c, swp=(i, c))))
        t = a[i]
        a[i] = a[c]
        fr.append((7, dict(vals=list(a), n=n, i=i, c=c, swp=(i, c))))
        a[c] = t
        fr.append((8, dict(vals=list(a), n=n, i=i, c=c, swp=(i, c))))
        i = c
        fr.append((9, dict(vals=list(a), n=n, i=i)))
    fr.append((2, dict(vals=list(a), n=n, i=i)))
    fr.append((11, dict(vals=list(a), n=n)))
    render(path, SIFT_DOWN, fr, draw_heap)


def gen_insert(path):
    a = [9, 7, 8, 3, 5, 2, 4]
    n0 = len(a)
    fr = [(1, dict(vals=list(a), n=n0))]
    a = a + [10]
    n = len(a)
    fr.append((1, dict(vals=list(a), n=n, i=7, new=7)))
    i = 7
    while i > 0:
        fr.append((2, dict(vals=list(a), n=n, i=i)))
        p = (i - 1) // 2
        fr.append((3, dict(vals=list(a), n=n, i=i, p=p)))
        fr.append((4, dict(vals=list(a), n=n, i=i, p=p, cmp=(p, i))))
        if a[p] >= a[i]:
            break
        fr.append((5, dict(vals=list(a), n=n, i=i, p=p, swp=(p, i))))
        t = a[p]
        a[p] = a[i]
        fr.append((6, dict(vals=list(a), n=n, i=i, p=p, swp=(p, i))))
        a[i] = t
        fr.append((7, dict(vals=list(a), n=n, i=i, p=p, swp=(p, i))))
        i = p
        fr.append((8, dict(vals=list(a), n=n, i=i)))
    fr.append((2, dict(vals=list(a), n=n, i=i)))
    fr.append((10, dict(vals=list(a), n=n)))
    render(path, SIFT_UP, fr, draw_heap)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen_siftdown(os.path.join(d, 'heap_siftdown.gif'))
    gen_insert(os.path.join(d, 'heap_insert.gif'))

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
from gif_common import render, cell, ptrbox, label, canvas, PTR

N = 8
W, H = 1.45, 1.7
X0 = 0.9
AY = 2.6

CODE = [
    "void push_back(Vector* v, int x) {",
    "    if (v->size == v->cap) {",
    "        v->cap = v->cap ? v->cap * 2 : 1;",
    "        v->data = realloc(v->data,",
    "                          v->cap * sizeof(int));",
    "    }",
    "    v->data[v->size] = x;",
    "    v->size++;",
    "}",
]


def draw_vec(ax, s):
    canvas(ax, (0, 13.4), (0.6, 6.58))
    vals, cap, size = s['vals'], s['cap'], s['size']
    ghost, new4 = s.get('ghost'), s.get('new4')
    copy, writing = s.get('copy'), s.get('writing')
    for k in range(N):
        x = X0 + k * W
        if k >= cap:
            ax.add_patch(mpatches.Rectangle(
                (x, AY), W, H, linewidth=1.1, edgecolor='#cccccc',
                facecolor='#fcfcfc', linestyle=(0, (4, 3))))
            label(ax, x + W / 2, AY - 0.3, str(k), color='#cccccc', fs=9)
            continue
        fc = '#f9f9f9'
        if ghost and k < 4:
            fc = '#e2e2e2'
            if copy is not None and k < copy:
                fc = '#f9f9f9'
        if new4 and k >= 4:
            fc = '#e8f5e9'
        if writing == k:
            fc = '#ffe0b2'
        if copy == k:
            fc = '#ffd54f'
        v = vals[k] if vals[k] is not None else ''
        cell(ax, x, AY, W, H, v, fc=fc, fs=15)
        label(ax, x + W / 2, AY - 0.3, str(k), color='#999999', fs=9)
    if writing is not None:
        ptrbox(ax, X0 + writing * W, AY, W, H, PTR[4], lw=3.2, pad=0.02)
    chips = [(0.6, 2.5, 'x = %s' % s['x'], PTR[4], '#fdf2e9'),
             (3.4, 3.0, 'size = %d' % size, PTR[0], '#fdecea'),
             (6.7, 2.9, 'cap = %d' % cap, PTR[1], '#eaf2fb')]
    for x0, w, txt, col, bg in chips:
        cell(ax, x0, 4.95, w, 0.85, txt, fc=bg, ec='#bbbbbb', fs=12)
        ptrbox(ax, x0, 4.95, w, 0.85, col, lw=2.6, pad=0.02)


def snap(vals, **kw):
    d = dict(vals=list(vals), size=0, cap=4, x='', ghost=False, new4=False,
             copy=None, writing=None)
    d.update(kw)
    return d


def gen(path):
    f = []
    vals = [None] * N
    size = 0

    def write_frame(v, **kw):
        vals[size] = v
        f.append((7, snap(vals, x=v, size=size, writing=size, **kw)))

    def size_frame(v, **kw):
        f.append((8, snap(vals, x=v, size=size + 1, **kw)))

    for v in (10, 20, 30, 40):
        f.append((1, snap(vals, x=v, size=size)))
        f.append((2, snap(vals, x=v, size=size)))
        write_frame(v)
        size += 1
        size_frame(v)

    f.append((1, snap(vals, x=50, size=size, cap=4)))
    f.append((2, snap(vals, x=50, size=size, cap=4)))
    f.append((3, snap(vals, x=50, size=size, cap=8, ghost=True, new4=True)))
    f.append((4, snap(vals, x=50, size=size, cap=8, ghost=True, new4=True)))
    for k in range(4):
        f.append((4, snap(vals, x=50, size=size, cap=8, ghost=True,
                          new4=True, copy=k)))
    write_frame(50, cap=8, new4=True)
    size += 1
    size_frame(50, cap=8, new4=True)

    f.append((1, snap(vals, x=60, size=size, cap=8)))
    f.append((2, snap(vals, x=60, size=size, cap=8)))
    write_frame(60, cap=8)
    size += 1
    size_frame(60, cap=8)
    render(path, CODE, f, draw_vec, interval=750)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen(os.path.join(d, 'vector_grow.gif'))

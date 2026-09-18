import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
from gif_common import render, cell, ptrbox, label, canvas, PTR

N = 8
W, H = 1.5, 1.1
X0 = 0.85
AY = 2.6
TOP = AY + H
MAXP = 1.3


def cx(i):
    return X0 + i * W + W / 2


CODE = [
    "int find(int* fa, int x) {",
    "    if (fa[x] == x) return x;",
    "    fa[x] = find(fa, fa[x]);",
    "    return fa[x];",
    "}",
    "void union_set(int* fa, int a, int b) {",
    "    int ra = find(fa, a);",
    "    int rb = find(fa, b);",
    "    if (ra != rb) fa[ra] = rb;",
    "}",
]


def arc(ax, x1, y1, x2, y2, color='#555555', lw=1.8, rad=0.5):
    ax.add_patch(mpatches.FancyArrowPatch(
        (x1, y1), (x2, y2), connectionstyle='arc3,rad=%.2f' % rad,
        arrowstyle='-|>', mutation_scale=13, color=color, lw=lw,
        shrinkA=0, shrinkB=0, zorder=1))


def self_loop(ax, x, y, color='#888888', lw=1.8):
    ax.add_patch(mpatches.FancyArrowPatch(
        (x - 0.3, y), (x + 0.3, y), connectionstyle='arc3,rad=-1.35',
        arrowstyle='-|>', mutation_scale=12, color=color, lw=lw,
        shrinkA=0, shrinkB=0, zorder=1))


def draw_uf(ax, s):
    canvas(ax, (0, 14), (0.2, 5.6))
    fa = s['fa']
    for i in range(N):
        fc = '#f9f9f9'
        if i in s.get('path', ()):
            fc = '#e3f2fd'
        if s.get('just') == i:
            fc = '#fff3cd'
        cell(ax, X0 + i * W, AY, W, H, fa[i], fc=fc, fs=15)
        label(ax, cx(i), AY - 0.32, str(i), color='#999999', fs=9)
    for i in range(N):
        t = fa[i]
        if t == i:
            self_loop(ax, cx(i), TOP)
        else:
            d = abs(cx(t) - cx(i))
            rad = min(0.5, 2 * MAXP / d)
            if cx(t) > cx(i):
                rad = -rad
            arc(ax, cx(i), TOP, cx(t), TOP, rad=rad)
    if s.get('a') is not None:
        ptrbox(ax, X0 + s['a'] * W, AY, W, H, PTR[4], pad=0.16)
    if s.get('b') is not None:
        ptrbox(ax, X0 + s['b'] * W, AY, W, H, PTR[5], pad=0.16)
    if s.get('x') is not None:
        ptrbox(ax, X0 + s['x'] * W, AY, W, H, PTR[0], pad=0.02)
    if s.get('ra') is not None:
        ptrbox(ax, X0 + s['ra'] * W, AY, W, H, PTR[2], pad=0.09)
    if s.get('rb') is not None:
        ptrbox(ax, X0 + s['rb'] * W, AY, W, H, PTR[3], pad=0.09)


def snap(fa, **kw):
    d = dict(fa=list(fa), x=None, just=None, path=(), a=None, b=None,
             ra=None, rb=None)
    d.update(kw)
    return d


def gen(path):
    fa = [0, 1, 1, 2, 3, 5, 6, 7]
    f = []

    def add(line, fa, **kw):
        f.append((line, snap(fa, **kw)))

    add(1, fa, x=4)
    add(2, fa, x=4, path=(4,))
    add(3, fa, x=4, path=(4,))
    add(2, fa, x=3, path=(4, 3))
    add(3, fa, x=3, path=(4, 3))
    add(2, fa, x=2, path=(4, 3, 2))
    add(3, fa, x=2, path=(4, 3, 2))
    add(2, fa, x=1, path=(4, 3, 2, 1))
    add(4, fa, x=1, path=(4, 3, 2, 1))
    add(3, fa, x=2, just=2)
    add(4, fa, x=2)
    fa3 = list(fa)
    fa3[3] = 1
    add(3, fa3, x=3, just=3)
    add(4, fa3, x=3)
    fa4 = list(fa3)
    fa4[4] = 1
    add(3, fa4, x=4, just=4)
    add(4, fa4, x=4)
    add(6, fa4, a=4, b=6)
    add(7, fa4, a=4, b=6, x=4)
    add(4, fa4, a=4, b=6, x=1)
    add(7, fa4, a=4, b=6, ra=1)
    add(8, fa4, a=4, b=6, ra=1, x=6)
    add(8, fa4, a=4, b=6, ra=1, rb=6)
    fa5 = list(fa4)
    fa5[1] = 6
    add(9, fa5, a=4, b=6, ra=1, rb=6, just=1)
    add(10, fa5)
    render(path, CODE, f, draw_uf)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen(os.path.join(d, 'union_find.gif'))

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
from gif_common import render, cell, ptrbox, label, canvas, PTR

W, H = 1.4, 1.6
X0 = 1.1
AY = 2.2
TOP = AY + H
N = 8
MAXP = 0.55

CODE = [
    "void update(int* c, int n, int i, int v) {",
    "    while (i <= n) {",
    "        c[i] += v;",
    "        i += i & -i;",
    "    }",
    "}",
    "int query(int* c, int i) {",
    "    int s = 0;",
    "    while (i > 0) {",
    "        s += c[i];",
    "        i -= i & -i;",
    "    }",
    "    return s;",
    "}",
]


def cx(k):
    return X0 + (k - 1) * W + W / 2


def draw_bit(ax, s):
    canvas(ax, (0, 13.2), (0.5, 6.4))
    c = s['c']
    i, cur = s.get('i'), s.get('cur')
    acc, upd = set(s.get('acc', ())), set(s.get('upd', ()))
    for k in range(1, N + 1):
        fc = '#f9f9f9'
        if k in upd:
            fc = '#fff3cd'
        if k in acc:
            fc = '#d5f5e3'
        if cur == k:
            fc = '#ffe082'
        cell(ax, X0 + (k - 1) * W, AY, W, H, c[k - 1], fc=fc, fs=14)
        label(ax, cx(k), AY - 0.3, str(k), color='#999999', fs=9)
    jump = s.get('jump')
    if jump:
        a, b = jump
        x1 = cx(a)
        if b > N:
            x2 = 12.9
        elif b < 1:
            x2 = 0.5
        else:
            x2 = cx(b)
        d = abs(x2 - x1)
        rad = min(0.45, 2 * MAXP / d)
        if x2 > x1:
            rad = -rad
        ax.add_patch(mpatches.FancyArrowPatch(
            (x1, TOP), (x2, TOP), connectionstyle='arc3,rad=%.2f' % rad,
            arrowstyle='-|>', mutation_scale=13, color=PTR[0], lw=2.2,
            shrinkA=0, shrinkB=0, zorder=1))
    if i is not None and 1 <= i <= N:
        ptrbox(ax, X0 + (i - 1) * W, AY, W, H, PTR[0], lw=3.2, pad=0.02)
    cell(ax, 0.5, 5.15, 2.4, 0.8, 'i = %d' % s.get('iv', 0), fc='#fdecea',
         ec='#bbbbbb', fs=12)
    ptrbox(ax, 0.5, 5.15, 2.4, 0.8, PTR[0], lw=2.6, pad=0.02)
    if s.get('phase') == 'update':
        cell(ax, 3.25, 5.15, 2.6, 0.8, 'v = +5', fc='#fdf2e9',
             ec='#bbbbbb', fs=12)
        ptrbox(ax, 3.25, 5.15, 2.6, 0.8, PTR[4], lw=2.6, pad=0.02)
    else:
        cell(ax, 3.25, 5.15, 2.9, 0.8, 's = %d' % s.get('s', 0),
             fc='#e9f7ef', ec='#bbbbbb', fs=12)
        ptrbox(ax, 3.25, 5.15, 2.9, 0.8, PTR[2], lw=2.6, pad=0.02)


C0 = [1, 3, 3, 10, 5, 11, 7, 36]


def snap(**kw):
    d = dict(c=list(C0), i=None, iv=0, cur=None, acc=(), upd=(),
             jump=None, s=0, phase='update')
    d.update(kw)
    return d


def gen(path):
    f = []
    c = list(C0)
    f.append((1, snap(c=c, i=3, iv=3, phase='update')))
    f.append((2, snap(c=c, i=3, iv=3)))
    c[2] += 5
    f.append((3, snap(c=c, i=3, iv=3, cur=3, upd=(3,))))
    f.append((4, snap(c=c, i=3, iv=3, upd=(3,), jump=(3, 4))))
    f.append((2, snap(c=c, i=4, iv=4, upd=(3,))))
    c[3] += 5
    f.append((3, snap(c=c, i=4, iv=4, cur=4, upd=(3, 4))))
    f.append((4, snap(c=c, i=4, iv=4, upd=(3, 4), jump=(4, 8))))
    f.append((2, snap(c=c, i=8, iv=8, upd=(3, 4))))
    c[7] += 5
    f.append((3, snap(c=c, i=8, iv=8, cur=8, upd=(3, 4, 8))))
    f.append((4, snap(c=c, i=8, iv=8, upd=(3, 4, 8), jump=(8, 16))))
    f.append((2, snap(c=c, i=16, iv=16, upd=(3, 4, 8))))
    f.append((6, snap(c=c, i=16, iv=16, upd=(3, 4, 8))))
    f.append((7, snap(c=c, i=7, iv=7, phase='query')))
    f.append((8, snap(c=c, i=7, iv=7, phase='query')))
    f.append((9, snap(c=c, i=7, iv=7, phase='query')))
    f.append((10, snap(c=c, i=7, iv=7, s=c[6], acc=(7,), cur=7,
                       phase='query')))
    f.append((11, snap(c=c, i=7, iv=7, s=c[6], acc=(7,), phase='query',
                       jump=(7, 6))))
    f.append((9, snap(c=c, i=6, iv=6, s=c[6], acc=(7,), phase='query')))
    f.append((10, snap(c=c, i=6, iv=6, s=c[6] + c[5], acc=(6, 7), cur=6,
                       phase='query')))
    f.append((11, snap(c=c, i=6, iv=6, s=c[6] + c[5], acc=(6, 7),
                       phase='query', jump=(6, 4))))
    f.append((9, snap(c=c, i=4, iv=4, s=c[6] + c[5], acc=(6, 7),
                      phase='query')))
    tot = c[6] + c[5] + c[3]
    f.append((10, snap(c=c, i=4, iv=4, s=tot, acc=(4, 6, 7), cur=4,
                       phase='query')))
    f.append((11, snap(c=c, i=4, iv=4, s=tot, acc=(4, 6, 7),
                       phase='query', jump=(4, 0))))
    f.append((9, snap(c=c, i=0, iv=0, s=tot, acc=(4, 6, 7),
                      phase='query')))
    f.append((13, snap(c=c, i=0, iv=0, s=tot, acc=(4, 6, 7),
                       phase='query')))
    f.append((14, snap(c=c, i=0, iv=0, s=tot, acc=(4, 6, 7),
                       phase='query')))
    render(path, CODE, f, draw_bit, interval=750)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen(os.path.join(d, 'bit_update_query.gif'))

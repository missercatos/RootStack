import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
from gif_common import render, cell, ptrbox, label, canvas, line, PTR

BUILD = [
    "void build(int* tree, int* a, int node, int l, int r) {",
    "    if (l == r) {",
    "        tree[node] = a[l];",
    "        return;",
    "    }",
    "    int mid = (l + r) / 2;",
    "    build(tree, a, node * 2, l, mid);",
    "    build(tree, a, node * 2 + 1, mid + 1, r);",
    "    tree[node] = tree[node * 2] + tree[node * 2 + 1];",
    "}",
]

QUERY = [
    "int query(int* tree, int node, int l, int r, int ql, int qr) {",
    "    if (qr < l || r < ql) return 0;",
    "    if (ql <= l && r <= qr) return tree[node];",
    "    int mid = (l + r) / 2;",
    "    return query(tree, node * 2, l, mid, ql, qr)",
    "         + query(tree, node * 2 + 1, mid + 1, r, ql, qr);",
    "}",
]

CODE = BUILD + [''] + QUERY
A = [3, 1, 4, 2]
POS = {1: (7.0, 5.7), 2: (3.6, 4.0), 3: (10.4, 4.0),
       4: (1.9, 2.3), 5: (5.3, 2.3), 6: (8.7, 2.3), 7: (12.1, 2.3)}
SEG = {1: (0, 3), 2: (0, 1), 3: (2, 3), 4: (0, 0), 5: (1, 1),
       6: (2, 2), 7: (3, 3)}
R = 0.58
QL, QR = 1, 3
CH = 0.85
CW = 1.5
AY = 0.45


def draw_tree(ax, s):
    canvas(ax, (0, 14), (0.4, 6.65))
    vals, cur = s['vals'], s.get('cur')
    visited, hit = s.get('visited', set()), s.get('hit', set())
    dead, src = s.get('dead', set()), s.get('src')
    for v, (l, r) in SEG.items():
        for ch in (2 * v, 2 * v + 1):
            if ch in POS:
                line(ax, POS[v][0], POS[v][1], POS[ch][0], POS[ch][1],
                     color='#666666', lw=1.6)
    for v in POS:
        x, y = POS[v]
        fc, ec, lw = '#ffffff', '#444444', 2
        if v in hit:
            fc, ec, lw = '#d5f5e3', PTR[2], 2.4
        elif v in dead:
            fc, ec = '#f0f0f0', '#b0b0b0'
        elif v in visited:
            fc = '#eaf2fb'
        ax.add_patch(mpatches.Circle((x, y), R, facecolor=fc, edgecolor=ec,
                                     linewidth=lw, zorder=2))
        if vals.get(v) is not None:
            ax.text(x, y, str(vals[v]), ha='center', va='center',
                    fontsize=13, fontweight='bold', zorder=3)
        l0, r0 = SEG[v]
        col = PTR[0] if v == cur else '#999999'
        label(ax, x, y - R - 0.28, '[%d,%d]' % (l0, r0), color=col,
              fs=9, weight='bold')
    if cur is not None:
        ax.add_patch(mpatches.Circle(POS[cur], R + 0.09, facecolor='none',
                                     edgecolor=PTR[0], linewidth=3.2,
                                     zorder=6))
    for i in range(4):
        x = POS[4 + i][0]
        fc = '#f9f9f9'
        if QL <= i <= QR and s.get('phase') == 'query':
            fc = '#f3e5f5'
        if src == i:
            fc = '#fff3cd'
        cell(ax, x - CW / 2, AY, CW, CH, A[i], fc=fc, fs=13)
        label(ax, x, AY - 0.28, str(i), color='#999999', fs=9)
    if s.get('phase') == 'query':
        cell(ax, 0.4, 5.8, 2.6, 0.72, '[%d, %d]' % (QL, QR), fc='#f6eafb',
             ec='#bbbbbb', fs=12)
        ptrbox(ax, 0.4, 5.8, 2.6, 0.72, PTR[3], lw=2.6, pad=0.02)
        cell(ax, 0.4, 4.85, 2.6, 0.72, 'ans = %d' % s.get('ans', 0),
             fc='#e9f7ef', ec='#bbbbbb', fs=12)
        ptrbox(ax, 0.4, 4.85, 2.6, 0.72, PTR[2], lw=2.6, pad=0.02)
    for v, txt in s.get('adds', ()):
        x, y = POS[v]
        label(ax, x + R + 0.32, y + R - 0.1, txt, color=PTR[2], fs=13)


def snap(vals, **kw):
    d = dict(vals=dict(vals), cur=None, visited=set(), hit=set(), dead=set(),
             ans=0, adds=(), phase='build', src=None)
    d.update(kw)
    return d


def gen(path):
    f = []
    vals = {}

    def add(line, node, **kw):
        f.append((line, snap(vals, cur=node, **kw)))

    add(1, 1)
    add(2, 1)
    add(6, 1)
    add(7, 2)
    add(6, 2)
    add(7, 4)
    add(2, 4)
    vals[4] = A[0]
    add(3, 4, src=0)
    add(8, 5)
    add(2, 5)
    vals[5] = A[1]
    add(3, 5, src=1)
    vals[2] = vals[4] + vals[5]
    add(9, 2)
    add(8, 3)
    add(6, 3)
    add(7, 6)
    add(2, 6)
    vals[6] = A[2]
    add(3, 6, src=2)
    add(8, 7)
    add(2, 7)
    vals[7] = A[3]
    add(3, 7, src=3)
    vals[3] = vals[6] + vals[7]
    add(9, 3)
    vals[1] = vals[2] + vals[3]
    add(9, 1)
    add(10, 1)

    vis, hit, dead, ans, adds = set(), set(), set(), 0, []

    def q(line, node, **kw):
        f.append((line, snap(vals, cur=node, phase='query', visited=set(vis),
                             hit=set(hit), dead=set(dead), ans=ans,
                             adds=tuple(adds), **kw)))

    q(12, 1)
    vis.add(1)
    q(13, 1)
    q(14, 1)
    q(16, 2)
    vis.add(2)
    q(15, 2)
    q(16, 4)
    vis.add(4)
    dead.add(4)
    q(13, 4)
    q(17, 5)
    vis.add(5)
    q(13, 5)
    ans += vals[5]
    hit.add(5)
    adds.append((5, '+%d' % vals[5]))
    q(14, 5)
    q(17, 3)
    vis.add(3)
    q(13, 3)
    ans += vals[3]
    hit.add(3)
    adds.append((3, '+%d' % vals[3]))
    q(14, 3)
    q(18, 1)
    render(path, CODE, f, draw_tree, interval=750)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen(os.path.join(d, 'segtree_build_query.gif'))

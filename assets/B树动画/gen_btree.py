import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
from gif_common import render, cell, ptrbox, label, canvas, line, PTR

CODE = [
    "void insert(BTree** root, int k) {",
    "    BTree* r = *root;",
    "    if (r->n == MAX) {",
    "        BTree* s = new_node();",
    "        s->child[0] = r;",
    "        split_child(s, 0);",
    "        *root = s;",
    "        r = s;",
    "    }",
    "    insert_nonfull(r, k);",
    "}",
]

KW, KH = 1.05, 0.85
NODE_COLOR = '#444444'


def bnode(ax, cx, cy, keys, ec=NODE_COLOR, lw=2.2, fc='#ffffff', hl=()):
    n = max(len(keys), 1)
    w = n * KW + 0.4
    x0 = cx - w / 2
    y0 = cy - KH / 2
    ax.add_patch(mpatches.FancyBboxPatch(
        (x0, y0), w, KH, boxstyle='round,pad=0.04', linewidth=lw,
        edgecolor=ec, facecolor=fc, zorder=2))
    if not keys:
        return w
    for j, k in enumerate(keys):
        kx = x0 + 0.2 + j * KW
        cf = '#e8f5e9' if j in hl else '#f9f9f9'
        ce = PTR[2] if j in hl else '#cccccc'
        cell(ax, kx, y0 + 0.13, KW, KH - 0.26, k, fc=cf, ec=ce, fs=14)
    return w


def draw(ax, s):
    canvas(ax, (0, 14), (0, 6))
    cell(ax, 0.9, 4.7, 1.5, 0.8, s['k'], fc='#ffffff', ec=PTR[1], lw=2, fs=15)
    ptrbox(ax, 0.9, 4.7, 1.5, 0.8, PTR[1], lw=2.6)
    label(ax, 1.65, 5.7, 'k', color=PTR[1], fs=12)

    nodes = s['nodes']
    for pid, cid in s['edges']:
        px, py, _ = nodes[pid]
        cx, cy, _ = nodes[cid]
        line(ax, px, py - KH / 2, cx, cy + KH / 2, color='#999999', lw=1.8)
    for nid in sorted(nodes):
        cx, cy, keys = nodes[nid]
        ec, lw, hl = NODE_COLOR, 2.2, ()
        if nid == s.get('full'):
            ec, lw = PTR[4], 3.0
        if nid == s.get('cur'):
            ec, lw = PTR[0], 3.4
        if nid == s.get('new'):
            ec, lw = PTR[2], 3.4
        if nid == s.get('target'):
            ec, lw = PTR[1], 3.2
        if nid == s.get('hl_node'):
            hl = (s.get('hl_key'),)
        w = bnode(ax, cx, cy, keys, ec=ec, lw=lw, hl=hl)
        if nid == s.get('cur'):
            ptrbox(ax, cx - w / 2 - 0.12, cy - KH / 2 - 0.12, w + 0.24,
                   KH + 0.24, PTR[0], lw=2.2, pad=0.02)
            label(ax, cx, cy - KH / 2 - 0.38, 'r', color=PTR[0], fs=12)
        if nid == s.get('new'):
            label(ax, cx, cy + KH / 2 + 0.32, 's', color=PTR[2], fs=12)
        if nid == s.get('target'):
            label(ax, cx, cy + KH / 2 + 0.32, 'r', color=PTR[1], fs=12)


def st(nodes, edges, k, **kw):
    d = dict(nodes={n: (c[0], c[1], list(c[2])) for n, c in nodes.items()},
             edges=list(edges), k=k)
    d.update(kw)
    return d


def gen(path):
    frames = []
    A = (7.0, 4.6)
    ROOT_TOP = (7.0, 5.15)
    LEFT = (4.5, 3.1)
    RIGHT = (9.5, 3.1)

    frames.append((1, st({0: (A[0], A[1], [])}, [], 10)))
    frames.append((2, st({0: (A[0], A[1], [])}, [], 10, cur=0)))
    frames.append((3, st({0: (A[0], A[1], [])}, [], 10, cur=0)))
    frames.append((10, st({0: (A[0], A[1], [10])}, [], 10, cur=0,
                          target=0, hl_node=0, hl_key=0)))

    frames.append((1, st({0: (A[0], A[1], [10])}, [], 20)))
    frames.append((2, st({0: (A[0], A[1], [10])}, [], 20, cur=0)))
    frames.append((3, st({0: (A[0], A[1], [10])}, [], 20, cur=0)))
    frames.append((10, st({0: (A[0], A[1], [10, 20])}, [], 20, cur=0,
                          target=0, hl_node=0, hl_key=1)))

    frames.append((1, st({0: (A[0], A[1], [10, 20])}, [], 30)))
    frames.append((2, st({0: (A[0], A[1], [10, 20])}, [], 30, cur=0)))
    frames.append((3, st({0: (A[0], A[1], [10, 20])}, [], 30, cur=0, full=0)))
    frames.append((4, st({0: (A[0], A[1], [10, 20]), 1: (ROOT_TOP[0],
                    ROOT_TOP[1], [])}, [], 30, cur=0, new=1, full=0)))
    frames.append((5, st({0: (LEFT[0], LEFT[1], [10, 20]), 1: (ROOT_TOP[0],
                    ROOT_TOP[1], [])}, [(1, 0)], 30, cur=0, new=1)))
    frames.append((6, st({1: (ROOT_TOP[0], ROOT_TOP[1], [20]),
                          0: (LEFT[0], LEFT[1], [10])}, [(1, 0)], 30,
                          cur=0, new=1, hl_node=1, hl_key=0)))
    frames.append((6, st({1: (ROOT_TOP[0], ROOT_TOP[1], [20]),
                          0: (LEFT[0], LEFT[1], [10]),
                          2: (RIGHT[0], RIGHT[1], [])}, [(1, 0), (1, 2)], 30,
                          cur=0, new=1)))
    frames.append((7, st({1: (ROOT_TOP[0], ROOT_TOP[1], [20]),
                          0: (LEFT[0], LEFT[1], [10]),
                          2: (RIGHT[0], RIGHT[1], [])}, [(1, 0), (1, 2)], 30,
                          cur=0, new=1)))
    frames.append((8, st({1: (ROOT_TOP[0], ROOT_TOP[1], [20]),
                          0: (LEFT[0], LEFT[1], [10]),
                          2: (RIGHT[0], RIGHT[1], [])}, [(1, 0), (1, 2)], 30,
                          new=1, target=1)))
    frames.append((10, st({1: (ROOT_TOP[0], ROOT_TOP[1], [20]),
                           0: (LEFT[0], LEFT[1], [10]),
                           2: (RIGHT[0], RIGHT[1], [30])}, [(1, 0), (1, 2)], 30,
                           target=2, hl_node=2, hl_key=0)))
    render(path, CODE, frames, draw)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen(os.path.join(d, 'btree_insert.gif'))

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
from gif_common import render, cell, ptrbox, label, canvas, line, circle_node, PTR

CODE = [
    "void insert(Trie* root, const char* w) {",
    "    Trie* p = root;",
    "    for (int i = 0; w[i]; i++) {",
    "        int c = w[i] - 'a';",
    "        if (p->child[c] == NULL) {",
    "            p->child[c] = new_node();",
    "        }",
    "        p = p->child[c];",
    "    }",
    "    p->end = 1;",
    "}",
]

POS = {0: (7.0, 5.35), 1: (4.0, 4.3), 2: (4.0, 3.2), 3: (2.6, 2.1),
       4: (5.4, 2.1), 5: (10.0, 4.3), 6: (10.0, 3.2), 7: (10.0, 2.1)}
CH = {1: 'c', 2: 'a', 3: 't', 4: 'r', 5: 'd', 6: 'o', 7: 'g'}
PAR = {1: 0, 2: 1, 3: 2, 4: 2, 5: 0, 6: 5, 7: 6}
R = 0.42
WORDS = ['cat', 'car', 'dog']


def draw(ax, s):
    canvas(ax, (0, 14), (0, 6))
    present, ends = s['present'], s['ends']
    for nid, par in PAR.items():
        if nid in present and par in present:
            x1, y1 = POS[par]
            x2, y2 = POS[nid]
            line(ax, x1, y1, x2, y2, color='#bbbbbb', lw=2)
    for nid in sorted(present):
        x, y = POS[nid]
        if nid == 0:
            circle_node(ax, x, y, '', r=0.2, fc='#555555', ec='#333333',
                        fs=10, lw=1.5)
            continue
        fc, ec, lw = '#ffffff', '#444444', 2
        if nid == s.get('peek'):
            fc = '#e8f0fe'
        if nid == s.get('new'):
            fc, ec, lw = '#e8f5e9', PTR[2], 3.4
        elif nid == s.get('cur'):
            fc, ec, lw = '#ffebee', PTR[0], 3.4
        if nid in ends:
            ax.add_patch(mpatches.Circle((x, y), R + 0.14, facecolor='none',
                                         edgecolor='#7f8c8d', linewidth=2,
                                         zorder=1))
        circle_node(ax, x, y, CH[nid], r=R, fc=fc, ec=ec, fs=14, lw=lw)
        if nid == s.get('cur'):
            ptrbox(ax, x - R - 0.08, y - R - 0.08, 2 * R + 0.16,
                   2 * R + 0.16, PTR[0], lw=2.2, pad=0.02)

    w = s.get('word')
    if w:
        n = len(w)
        cw, chh = 0.85, 0.85
        x0 = 7.0 - n * cw / 2
        y = 0.55
        for k in range(n):
            cell(ax, x0 + k * cw, y, cw, chh, w[k], fc='#f9f9f9', fs=15)
            label(ax, x0 + k * cw + cw / 2, y - 0.22, str(k),
                  color='#999999', fs=9)
        i = s.get('i')
        if i is not None:
            ptrbox(ax, x0 + i * cw, y, cw, chh, PTR[1], lw=2.6)
            label(ax, x0 + i * cw + cw / 2, y + chh + 0.3, 'c',
                  color=PTR[1], fs=12)


def st(present, ends, word=None, i=None, cur=None, new=None, peek=None):
    return dict(present=set(present), ends=set(ends), word=word, i=i,
                cur=cur, new=new, peek=peek)


def find_child(p, ch, present):
    for nid, par in PAR.items():
        if par == p and CH[nid] == ch and nid in present:
            return nid
    return None


def next_id(present):
    for nid in sorted(CH):
        if nid not in present:
            return nid
    return None


def gen(path):
    frames = []
    present = {0}
    ends = set()
    frames.append((1, st(present, ends)))
    for w in WORDS:
        p = 0
        frames.append((3, st(present, ends, word=w, cur=p)))
        for i, ch in enumerate(w):
            frames.append((4, st(present, ends, word=w, i=i, cur=p)))
            child = find_child(p, ch, present)
            frames.append((5, st(present, ends, word=w, i=i, cur=p,
                                   peek=child)))
            if child is None:
                nid = next_id(present)
                present = present | {nid}
                frames.append((6, st(present, ends, word=w, i=i, cur=p,
                                     new=nid)))
                child = nid
            frames.append((8, st(present, ends, word=w, i=i, cur=child)))
            p = child
        ends = ends | {p}
        frames.append((10, st(present, ends, word=w, cur=p)))
    frames.append((11, st(present, ends)))
    render(path, CODE, frames, draw)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen(os.path.join(d, 'trie_insert.gif'))

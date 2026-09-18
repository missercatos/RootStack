import os
import matplotlib
matplotlib.use('Agg')
from gif_common import render, cell, ptrbox, label, canvas, arrow, PTR

CODE = [
    "void insert(HashTable* ht, int key) {",
    "    int i = key % M;",
    "    Node* p = malloc(sizeof(Node));",
    "    p->key = key;",
    "    p->next = ht->bucket[i];",
    "    ht->bucket[i] = p;",
    "}",
]

M = 7
BX, BY0, BW, BH = 3.2, 5.3, 1.2, 0.6
STEP = 0.72
NW, NH = 0.95, 0.5
NX0 = BX + BW + 0.45
NSTEP = 1.12
KEYS = [8, 15, 1, 22, 10]


def draw(ax, s):
    canvas(ax, (0, 14), (0, 6))
    cell(ax, 0.6, 4.9, 1.5, 0.8, s['key'], fc='#ffffff', ec=PTR[1],
         lw=2, fs=15)
    ptrbox(ax, 0.6, 4.9, 1.5, 0.8, PTR[1], lw=2.6)
    label(ax, 1.35, 5.9, 'key', color=PTR[1], fs=12)
    i = s.get('i')
    cell(ax, 0.6, 3.5, 1.5, 0.8, '' if i is None else i, fc='#ffffff',
         ec=PTR[4], lw=2, fs=15)
    ptrbox(ax, 0.6, 3.5, 1.5, 0.8, PTR[4], lw=2.6)
    label(ax, 1.35, 4.5, 'i', color=PTR[4], fs=12)

    chains = s['chains']
    for b in range(M):
        y = BY0 - b * STEP
        label(ax, BX - 0.18, y + BH / 2, str(b), color='#999999', fs=10,
              ha='right')
        cell(ax, BX, y, BW, BH, '', fc='#fff3e0' if b == i else '#f9f9f9',
             fs=12)
        if b == i:
            ptrbox(ax, BX, y, BW, BH, PTR[4], lw=2.4)
        lst = chains.get(b, [])
        for j, v in enumerate(lst):
            nx = NX0 + j * NSTEP
            ny = y + (BH - NH) / 2
            is_new = s.get('newpos') == (b, j)
            cell(ax, nx, ny, NW, NH, v, fc='#e8f5e9' if is_new else '#ffffff',
                 fs=13)
            if is_new:
                ptrbox(ax, nx, ny, NW, NH, PTR[2], lw=2.6)
        if not lst:
            continue
        head = s['bhead'].get(b)
        if head is not None:
            hx = NX0 + head * NSTEP
            arrow(ax, BX + BW + 0.06, y + BH / 2, hx - 0.05, y + BH / 2,
                  color='#888888', lw=1.6)
        for j in range(len(lst) - 1):
            if j == 0 and s.get('newpos') == (b, 0) and not s.get('pnext'):
                continue
            arrow(ax, NX0 + j * NSTEP + NW + 0.05, y + BH / 2,
                  NX0 + (j + 1) * NSTEP - 0.05, y + BH / 2,
                  color='#888888', lw=1.6)


def st(chains, bhead, key, i=None, newpos=None, pnext=False):
    return dict(chains={k: list(v) for k, v in chains.items()},
                bhead=dict(bhead), key=key, i=i, newpos=newpos, pnext=pnext)


def gen(path):
    chains, bhead = {}, {}
    frames = []
    for key in KEYS:
        b = key % M
        old = chains.get(b, [])
        frames.append((1, st(chains, bhead, key)))
        frames.append((2, st(chains, bhead, key, i=b)))
        disp = dict(chains)
        disp[b] = [''] + list(old)
        bh = dict(bhead)
        if old:
            bh[b] = 1
        frames.append((3, st(disp, bh, key, i=b, newpos=(b, 0))))
        disp[b] = [key] + list(old)
        frames.append((4, st(disp, bh, key, i=b, newpos=(b, 0))))
        frames.append((5, st(disp, bh, key, i=b, newpos=(b, 0), pnext=True)))
        chains[b] = [key] + list(old)
        bhead[b] = 0
        frames.append((6, st(chains, bhead, key, i=b, newpos=(b, 0))))
    render(path, CODE, frames, draw)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen(os.path.join(d, 'hash_chaining.gif'))

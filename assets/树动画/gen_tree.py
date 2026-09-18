import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
from gif_common import render, cell, ptrbox, label, canvas, line, arrow, circle_node, PTR

# ================= 二叉搜索树插入 =================
BST_CODE = [
    "Node* insert(Node* root, int x) {",
    "    if (root == NULL)",
    "        return new_node(x);",
    "    if (x < root->data)",
    "        root->left = insert(root->left, x);",
    "    else if (x > root->data)",
    "        root->right = insert(root->right, x);",
    "    return root;",
    "}",
]

BX = {20: 1.6, 30: 3.8, 40: 6.0, 50: 8.2, 60: 10.4, 70: 12.6}
BD = {50: 0, 30: 1, 70: 1, 20: 2, 40: 2, 60: 2}
BR = 0.5


def bx(v):
    return BX[v]


def by(v):
    return 5.9 - BD[v] * 1.45


def byd(d):
    return 5.9 - d * 1.45


def bst_dir_arrow(ax, v, d):
    x, y = bx(v), by(v)
    dx = -1.15 if d == 'L' else 1.15
    arrow(ax, x + dx * 0.5, y - 0.42, x + dx, y - 0.95,
          color='#e67e22', lw=2.2)


def draw_bst(ax, s):
    canvas(ax, (0, 14), (0.9, 6.9))
    cell(ax, 0.4, 5.75, 2.3, 0.85, "x = %d" % s['x'], fc='#ffffff',
         ec=PTR[1], lw=2, fs=14)
    ptrbox(ax, 0.4, 5.75, 2.3, 0.85, PTR[1], lw=2)
    tree, cur, new = s['tree'], s.get('cur'), s.get('new')
    path = s.get('path') or set()
    for v, (l, r) in tree.items():
        for ch in (l, r):
            if ch is not None:
                line(ax, bx(v), by(v), bx(ch), by(ch))
    for v in tree:
        x, y = bx(v), by(v)
        fc, ec, lw = '#ffffff', '#444444', 2
        if v in path:
            fc = '#e8f0fe'
        if v == new:
            fc, ec, lw = '#e8f5e9', PTR[2], 3.6
        elif v == cur:
            fc, ec, lw = '#ffebee', PTR[0], 3.6
        circle_node(ax, x, y, v, r=BR, fc=fc, ec=ec, fs=12, lw=lw)
    if cur is not None:
        label(ax, bx(cur), by(cur) + BR + 0.3, 'cur', color=PTR[0], fs=12)
    if new is not None:
        label(ax, bx(new), by(new) + BR + 0.3, 'new', color=PTR[2], fs=12)
    if s.get('slot') is not None and new is None:
        ax.add_patch(mpatches.Circle((bx(s['x']), byd(BD[s['x']])), BR,
                                     facecolor='none', edgecolor='#bbbbbb',
                                     linewidth=2, linestyle='--', zorder=1))
    if cur is not None and s.get('dir'):
        bst_dir_arrow(ax, cur, s['dir'])


def gen_bst(path):
    tree = {}
    frames = []

    def snap(line, tree, x, cur=None, new=None, path=(), dir=None, slot=False):
        return (line, dict(tree={k: list(v) for k, v in tree.items()}, x=x,
                           cur=cur, new=new, path=set(path), dir=dir,
                           slot=x if slot else None))

    for x in [50, 30, 70, 20, 40, 60]:
        frames.append(snap(1, tree, x))
        seen = []
        node = 50 if tree else None
        parent, d = None, None
        while node is not None:
            frames.append(snap(2, tree, x, cur=node, path=seen))
            seen.append(node)
            if x < node:
                frames.append(snap(4, tree, x, cur=node, path=seen, dir='L'))
                parent, d = node, 0
                node = tree[node][0]
            else:
                frames.append(snap(6, tree, x, cur=node, path=seen, dir='R'))
                parent, d = node, 1
                node = tree[node][1]
        frames.append(snap(2, tree, x, path=seen, slot=True))
        tree[x] = [None, None]
        if parent is not None:
            tree[parent][d] = x
        frames.append(snap(3, tree, x, new=x, path=seen))
        frames.append(snap(8, tree, x, path=seen))
    render(path, BST_CODE, frames, draw_bst)


# ================= 非递归中序遍历 =================
IN_CODE = [
    "void inorder(Node* root) {",
    "    Node* st[100]; int top = -1;",
    "    Node* cur = root;",
    "    while (cur != NULL || top >= 0) {",
    "        while (cur != NULL) {",
    "            st[++top] = cur;",
    "            cur = cur->left;",
    "        }",
    "        cur = st[top--];",
    "        visit(cur);",
    "        cur = cur->right;",
    "    }",
    "}",
]

VAL = [1, 2, 3, 4, 5, 6, 7]
IDX = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6}
DEP = {4: 0, 2: 1, 6: 1, 1: 2, 3: 2, 5: 2, 7: 2}
LEFT = {4: 2, 2: 1, 1: None, 3: None, 6: 5, 5: None, 7: None}
RIGHT = {4: 6, 2: 3, 1: None, 3: None, 6: 7, 5: None, 7: None}
TR = 0.48
SX, SY, SW, SH, SG = 0.7, 2.4, 1.35, 0.9, 1.45
OX, OW, OG = 6.0, 1.0, 1.05


def tx(v):
    return 1.8 + IDX[v] * 1.85


def ty(v):
    return 7.3 - DEP[v] * 1.25


def draw_inorder(ax, s):
    canvas(ax, (0, 14), (1.6, 8.25))
    cur, stack, out = s['cur'], s['stack'], s['out']
    visited, hl = s['visited'], s['hl']
    for v in VAL:
        for ch in (LEFT[v], RIGHT[v]):
            if ch is not None:
                line(ax, tx(v), ty(v), tx(ch), ty(ch))
    for v in VAL:
        x, y = tx(v), ty(v)
        if v == cur:
            circle_node(ax, x, y, v, r=TR, fc='#ffebee', ec=PTR[0], fs=12, lw=3.6)
        elif v in visited:
            circle_node(ax, x, y, v, r=TR, fc='#d9d9d9', ec='#9e9e9e', fs=12, lw=2)
        else:
            circle_node(ax, x, y, v, r=TR, fc='#ffffff', ec='#444444', fs=12, lw=2)
    if cur is not None:
        label(ax, tx(cur), ty(cur) + TR + 0.32, 'cur', color=PTR[0], fs=12)
    for k in range(3):
        v = stack[k] if k < len(stack) else ''
        cell(ax, SX + k * SG, SY, SW, SH, v, fc='#f2f2f2', fs=13)
        label(ax, SX + k * SG + SW / 2, SY - 0.4, str(k), color='#999999', fs=9)
    if stack:
        k = len(stack) - 1
        ptrbox(ax, SX + k * SG, SY, SW, SH, PTR[1])
        label(ax, SX + k * SG + SW / 2, SY + SH + 0.32, 'top', color=PTR[1], fs=12)
    else:
        label(ax, SX + SW / 2, SY + SH + 0.32, 'top=-1', color=PTR[1], fs=10)
    for k in range(7):
        v = out[k] if k < len(out) else ''
        fc = '#fff3cd' if k == hl else '#f9f9f9'
        cell(ax, OX + k * OG, SY, OW, SH, v, fc=fc, fs=13)


def gen_inorder(path):
    frames = []
    stack, out, visited = [], [], set()
    cur = None

    def snap(line, cur, hl=False):
        return (line, dict(cur=cur, stack=list(stack), out=list(out),
                           visited=set(visited), hl=len(out) - 1 if hl else -1))

    frames.append(snap(1, None))
    frames.append(snap(2, None))
    cur = 4
    frames.append(snap(3, cur))
    while cur is not None or stack:
        frames.append(snap(4, cur))
        inner = True
        while cur is not None:
            if inner:
                frames.append(snap(5, cur))
                inner = False
            stack.append(cur)
            frames.append(snap(6, cur))
            cur = LEFT[cur]
            frames.append(snap(7, cur))
        cur = stack.pop()
        frames.append(snap(9, cur))
        out.append(cur)
        visited.add(cur)
        frames.append(snap(10, cur, hl=True))
        cur = RIGHT[cur]
        frames.append(snap(11, cur))
    frames.append(snap(4, cur))
    frames.append(snap(13, cur))
    render(path, IN_CODE, frames, draw_inorder)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen_bst(os.path.join(d, 'bst_insert.gif'))
    gen_inorder(os.path.join(d, 'inorder_traversal.gif'))

"""单链表动画 GIF 生成脚本（生成后统一删除）"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as patches
from gif_common import (render, cell, ptrbox, label, arrow, canvas,
                        PTR, YELLOW, YELLOW_EDGE)

NODE_W, NODE_H = 3.0, 1.6
NULL_W, NULL_H = 1.9, 1.2
EC = '#555555'
FC = '#ffffff'
PFC = '#e9edf2'
ARROW = '#666666'
FLIP = '#e67e22'
RED = PTR[0]
BLUE = PTR[1]
GREEN = PTR[2]


def node(ax, cx, cy, val, w=NODE_W, h=NODE_H, fs=16):
    x, y = cx - w / 2.0, cy - h / 2.0
    dw = w * 0.64
    cell(ax, x, y, dw, h, val, fc=FC, ec=EC, lw=1.8, fs=fs)
    cell(ax, x + dw, y, w - dw, h, '', fc=PFC, ec=EC, lw=1.8)
    label(ax, x + dw + (w - dw) / 2.0, cy, '.', fs=20, color='#9aa4ad')


def pbox(ax, cx, cy, w, h, color, pad):
    ptrbox(ax, cx - w / 2.0, cy - h / 2.0, w, h, color, lw=3.5, pad=pad)


def hlink(ax, x1, x2, y1, y2, color=ARROW, lw=1.8, gap=0.15,
          w1=NODE_W, w2=NODE_W):
    if x2 >= x1:
        xa, xb = x1 + w1 / 2.0 + gap, x2 - w2 / 2.0 - gap
    else:
        xa, xb = x1 - w1 / 2.0 - gap, x2 + w2 / 2.0 + gap
    arrow(ax, xa, y1, xb, y2, color=color, lw=lw)


# ---------------------------------------------------------------- 插入
INSERT_CODE = [
    "void insert_after(Node* p, int x) {",
    "    Node* s = malloc(sizeof(Node));",
    "    s->data = x;",
    "    s->next = p->next;",
    "    p->next = s;",
    "}",
]
IX = [2.6, 7.2, 11.8]
IY = 7.4
IVALS = [10, 20, 30]
SX, SY = 7.2, 3.0


def draw_insert(ax, st):
    canvas(ax, (-0.5, 20.5), (1.0, 9.7))
    for k, cx in enumerate(IX):
        node(ax, cx, IY, IVALS[k])
    hlink(ax, IX[0], IX[1], IY, IY)
    if st['p_to'] == 'n3':
        hlink(ax, IX[1], IX[2], IY, IY)
    if st['s'] is not None:
        node(ax, SX, SY, st['s'])
        if st['s_next']:
            arrow(ax, SX + NODE_W / 2 + 0.1, SY + NODE_H / 3,
                  IX[2] - NODE_W / 2 + 0.55, IY - NODE_H / 2 - 0.12,
                  color=BLUE, lw=2.2)
    if st['p_to'] == 's':
        arrow(ax, SX, IY - NODE_H / 2 - 0.18, SX, SY + NODE_H / 2 + 0.18,
              color=RED, lw=2.2)
    if st['p']:
        pbox(ax, IX[1], IY, NODE_W, NODE_H, RED, 0.04)
    if st['s_box']:
        pbox(ax, SX, SY, NODE_W, NODE_H, BLUE, 0.04)


def gen_insert(path):
    base = dict(p=False, s=None, s_box=False, s_next=False, p_to='n3')
    frames = [
        (1, dict(base)),
        (1, dict(base, p=True)),
        (2, dict(base, p=True, s='')),
        (2, dict(base, p=True, s='', s_box=True)),
        (3, dict(base, p=True, s=99, s_box=True)),
        (4, dict(base, p=True, s=99, s_box=True, s_next=True)),
        (5, dict(base, p=True, s=99, s_box=True, s_next=True,
                 p_to='cut')),
        (5, dict(base, p=True, s=99, s_box=True, s_next=True, p_to='s')),
        (6, dict(base, p=True, s=99, s_box=True, s_next=True, p_to='s')),
    ]
    render(path, INSERT_CODE, frames, draw_insert, interval=650)


# ---------------------------------------------------------------- 反转
REVERSE_CODE = [
    "Node* reverse(Node* head) {",
    "    Node* prev = NULL;",
    "    while (head != NULL) {",
    "        Node* next = head->next;",
    "        head->next = prev;",
    "        prev = head;",
    "        head = next;",
    "    }",
    "    return prev;",
    "}",
]
RX = [4.2, 8.0, 11.8, 15.6]
RY = 6.3
NULL_C = (1.1, 6.3)


def draw_reverse(ax, st):
    canvas(ax, (-0.3, 20.6), (2.2, 10.4))
    x, y = NULL_C
    cell(ax, x - NULL_W / 2, y - NULL_H / 2, NULL_W, NULL_H, 'NULL',
         fc='#f4f4f4', ec='#aaaaaa', lw=1.4, fs=10, tc='#888888')
    for k, cx in enumerate(RX):
        node(ax, cx, RY, k + 1)
    for src, dst in sorted(st['links'].items()):
        col = FLIP if src in st['flip'] else ARROW
        lw = 2.2 if src in st['flip'] else 1.8
        if dst == 'L':
            hlink(ax, RX[src], NULL_C[0], RY, RY, color=col, lw=lw,
                  w2=NULL_W)
        else:
            hlink(ax, RX[src], RX[dst], RY, RY, color=col, lw=lw)
    for key, color, pad in (('head', RED, 0.04), ('next', GREEN, 0.30),
                            ('prev', BLUE, 0.56)):
        v = st[key]
        if v is None:
            continue
        if v == 'L':
            pbox(ax, NULL_C[0], NULL_C[1], NULL_W, NULL_H, color, pad)
        else:
            pbox(ax, RX[v], RY, NODE_W, NODE_H, color, pad)


def st_rev(head, prev, nxt, links, flip):
    return dict(head=head, prev=prev, next=nxt, links=dict(links),
                flip=set(flip))


def gen_reverse(path):
    links = {0: 1, 1: 2, 2: 3}
    flip = set()
    frames = [(1, st_rev(0, None, None, links, flip)),
              (2, st_rev(0, 'L', None, links, flip))]
    for it in range(4):
        frames.append((3, st_rev(it, it - 1 if it else 'L', None,
                                 links, flip)))
        nxt = links.get(it, 'L')
        frames.append((4, st_rev(it, it - 1 if it else 'L', nxt,
                                 links, flip)))
        links[it] = it - 1 if it else 'L'
        flip.add(it)
        frames.append((5, st_rev(it, it - 1 if it else 'L', nxt,
                                 links, flip)))
        frames.append((6, st_rev(it, it, nxt, links, flip)))
        head = nxt if nxt != 'L' else 'L'
        frames.append((7, st_rev(head, it, nxt, links, flip)))
    frames.append((3, st_rev('L', 3, 'L', links, flip)))
    frames.append((9, st_rev(None, 3, None, links, flip)))
    render(path, REVERSE_CODE, frames, draw_reverse, interval=500)


# ---------------------------------------------------------------- 判环
CYCLE_CODE = [
    "int has_cycle(Node* head) {",
    "    Node* slow = head;",
    "    Node* fast = head;",
    "    while (fast != NULL && fast->next != NULL) {",
    "        slow = slow->next;",
    "        fast = fast->next->next;",
    "        if (slow == fast) return 1;",
    "    }",
    "    return 0;",
    "}",
]
CX = [2.4, 6.2, 10.0, 14.4, 18.1]
CY = [4.4, 4.4, 4.4, 7.8, 4.4]


def curve_arrow(ax, p1, p2, rad, color=ARROW, lw=1.8):
    ax.add_patch(patches.FancyArrowPatch(
        p1, p2, arrowstyle='-|>', mutation_scale=14,
        connectionstyle=f'arc3,rad={rad}', color=color, lw=lw,
        shrinkA=0, shrinkB=0))


def draw_cycle(ax, st):
    canvas(ax, (-0.5, 20.7), (0.1, 9.7))
    for k in range(5):
        node(ax, CX[k], CY[k], k + 1)
    hlink(ax, CX[0], CX[1], CY[0], CY[1])
    hlink(ax, CX[1], CX[2], CY[1], CY[2])
    curve_arrow(ax, (CX[2] + 0.45, CY[2] + 0.72),
                (CX[3] - 0.75, CY[3] - 0.70), 0.22)
    curve_arrow(ax, (CX[3] + 0.75, CY[3] - 0.70),
                (CX[4] - 0.75, CY[4] + 0.70), 0.22)
    curve_arrow(ax, (CX[4] - 0.55, CY[4] - 0.70),
                (CX[2] + 0.55, CY[2] - 0.70), -0.42)
    if st['meet']:
        ax.add_patch(patches.Circle((CX[3], CY[3]), 1.95, facecolor=YELLOW,
                                    edgecolor=YELLOW_EDGE, lw=4.5, alpha=0.5,
                                    zorder=0))
    for key, color, pad in (('slow', RED, 0.04), ('fast', BLUE, 0.30)):
        v = st[key]
        pbox(ax, CX[v], CY[v], NODE_W, NODE_H, color, pad)


def gen_cycle(path):
    frames = [
        (1, dict(slow=0, fast=0, meet=False)),
        (2, dict(slow=0, fast=0, meet=False)),
        (3, dict(slow=0, fast=0, meet=False)),
    ]
    steps = [(4, 0, 0), (5, 1, 0), (6, 1, 2), (7, 1, 2),
             (4, 1, 2), (5, 2, 2), (6, 2, 4), (7, 2, 4),
             (4, 2, 4), (5, 3, 4), (6, 3, 3),
             (7, 3, 3), (7, 3, 3)]
    for line, slow, fast in steps:
        frames.append((line, dict(slow=slow, fast=fast,
                                  meet=line >= 7)))
    render(path, CYCLE_CODE, frames, draw_cycle, interval=450)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen_insert(os.path.join(d, 'list_insert.gif'))
    gen_reverse(os.path.join(d, 'list_reverse.gif'))
    gen_cycle(os.path.join(d, 'cycle_detect.gif'))

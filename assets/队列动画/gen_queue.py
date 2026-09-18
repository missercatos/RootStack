import os
import matplotlib.patches as patches
from gif_common import render, cell, ptrbox, label, canvas, PTR

M = 6
W, H = 1.0, 0.95
BASE_Y = 0.9
FILL, HOT, FULL = '#f9f9f9', '#fff8e1', '#ffcdd2'

CODE = [
    "int enqueue(int* q, int* front, int* rear, int x) {",
    "    if ((*rear + 1) % M == *front) return 0;",
    "    q[*rear] = x;",
    "    *rear = (*rear + 1) % M;",
    "    return 1;",
    "}",
    "int dequeue(int* q, int* front, int* rear, int* x) {",
    "    if (*front == *rear) return 0;",
    "    *x = q[*front];",
    "    *front = (*front + 1) % M;",
    "    return 1;",
    "}",
]


def draw(ax, s):
    canvas(ax, (-1.0, M * W + 1.0), (-1.0, 3.0))
    ax.add_patch(patches.FancyArrowPatch(
        (M * W - 0.05, 2.2), (-0.05, 2.2), connectionstyle='arc3,rad=0.2',
        arrowstyle='<|-|>', mutation_scale=12, color='#b0bec5', lw=1.6))
    for k in range(M):
        v = s['q'][k]
        fc = HOT if s['hot'] == k else (FULL if s['blocked'] == k else FILL)
        cell(ax, k * W, BASE_Y, W, H, '' if v is None else v, fc=fc, fs=14)
        label(ax, k * W + W / 2, BASE_Y - 0.32, str(k),
              color='#999999', fs=9)
    ptrbox(ax, s['rear'] * W, BASE_Y, W, H, PTR[1], pad=0.08)
    ptrbox(ax, s['front'] * W, BASE_Y, W, H, PTR[0], pad=0.015)


def gen(path):
    q = [None] * M
    front = rear = 0
    frames = []

    def snap(line, **kw):
        st = dict(q=list(q), front=front, rear=rear, hot=None, blocked=None)
        st.update(kw)
        frames.append((line, st))

    snap(1)
    for x in (11, 22, 33):
        snap(2)
        q[rear] = x
        snap(3, hot=rear)
        rear = (rear + 1) % M
        snap(4)
    snap(8)
    snap(9, hot=front)
    old = front
    q[old] = None
    front = (front + 1) % M
    snap(10)
    for x in (44, 55, 66):
        snap(2)
        q[rear] = x
        snap(3, hot=rear)
        rear = (rear + 1) % M
        snap(4)
    snap(2, blocked=(rear + 1) % M)
    snap(5, blocked=(rear + 1) % M)
    render(path, CODE, frames, draw, interval=450)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen(os.path.join(d, 'circular_queue.gif'))

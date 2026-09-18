import os
import matplotlib
matplotlib.use('Agg')
from gif_common import (render, cell, ptrbox, label, canvas, line, arrow,
                        circle_node, PTR)

GREY = '#dddddd'
NEW_FC = '#dcedc8'
OUT_FC = '#e0e0e0'
CUR = PTR[2]
EDGE_C = PTR[4]
FRONT_C = PTR[0]
REAR_C = PTR[1]

TOPO_CODE = [
    "int topo_sort(int g[][N], int n, int* order) {",
    "    int indeg[N] = {0}, q[N];",
    "    int front = 0, rear = 0, k = 0;",
    "    for (int u = 0; u < n; u++)",
    "        for (int v = 0; v < n; v++)",
    "            if (g[u][v]) indeg[v]++;",
    "    for (int u = 0; u < n; u++)",
    "        if (indeg[u] == 0) q[rear++] = u;",
    "    while (front < rear) {",
    "        int u = q[front++];",
    "        order[k++] = u;",
    "        for (int v = 0; v < n; v++)",
    "            if (g[u][v] && --indeg[v] == 0)",
    "                q[rear++] = v;",
    "    }",
    "    return k;",
    "}",
]

T_XY = {0: (1.0, 6.6), 1: (3.2, 7.9), 2: (3.2, 5.3),
        3: (5.4, 6.6), 4: (7.4, 7.9), 5: (5.4, 3.9)}
T_ADJ = {0: [1, 2], 1: [3], 2: [3, 5], 3: [4], 4: [], 5: []}
T_E = [(0, 1), (0, 2), (1, 3), (2, 3), (2, 5), (3, 4)]
R = 0.32
CW, CH, CX0 = 1.15, 0.85, 1.0
ROW_IDX, ROW_Q, ROW_ORD = 2.5, 1.45, 0.4


def draw_topo(ax, s):
    canvas(ax, (0.4, 8.4), (0.0, 8.3))
    for a, b in T_E:
        x1, y1 = T_XY[a]
        x2, y2 = T_XY[b]
        dx, dy = x2 - x1, y2 - y1
        d = (dx * dx + dy * dy) ** 0.5
        act = s.get('edge') == (a, b)
        line(ax, x1, y1, x2, y2, color=EDGE_C if act else '#888888',
             lw=4 if act else 2)
        arrow(ax, x1 + dx / d * R, y1 + dy / d * R,
              x2 - dx / d * R, y2 - dy / d * R,
              color=EDGE_C if act else '#888888', lw=3 if act else 1.6)
    for v in T_XY:
        fc = OUT_FC if v in s['done'] else '#ffffff'
        circle_node(ax, T_XY[v][0], T_XY[v][1], v, r=R, fc=fc, lw=2)
    if s.get('u') is not None:
        x, y = T_XY[s['u']]
        ptrbox(ax, x - R, y - R, 2 * R, 2 * R, CUR, lw=3, pad=0.06)
    for i in range(6):
        x = CX0 + i * CW
        fc = '#f9f9f9'
        if s['indeg'][i] == 0:
            fc = NEW_FC
        if s.get('upd') == i:
            fc = '#ffe0b2'
        cell(ax, x, ROW_IDX, CW, CH, s['indeg'][i], fc=fc, fs=14)
        v = s['q'][i] if i < len(s['q']) else ''
        qf = '#e3f2fd' if v != '' else '#f9f9f9'
        if i < s['front']:
            qf = '#eeeeee'
        cell(ax, x, ROW_Q, CW, CH, v, fc=qf, fs=14,
             tc='#aaaaaa' if i < s['front'] else 'black')
        o = s['order'][i] if i < len(s['order']) else ''
        cell(ax, x, ROW_ORD, CW, CH, o, fc=NEW_FC if o != '' else '#f9f9f9',
             fs=14)
    if s['front'] < 6:
        ptrbox(ax, CX0 + s['front'] * CW, ROW_Q, CW, CH, FRONT_C, pad=0.015)
    if s['rear'] < 6:
        ptrbox(ax, CX0 + s['rear'] * CW, ROW_Q, CW, CH, REAR_C, pad=0.06)


def topo_frames():
    indeg = [0] * 6
    q, front, order, done, fr = [], 0, [], set(), []

    def snap(ln, **kw):
        st = dict(indeg=list(indeg), q=list(q), front=front, rear=len(q),
                  order=list(order), done=set(done))
        st.update(kw)
        fr.append((ln, st))

    snap(2)
    snap(3)
    for u in range(6):
        if not T_ADJ[u]:
            continue
        snap(4, u=u)
        for v in T_ADJ[u]:
            indeg[v] += 1
            snap(6, u=u, edge=(u, v), upd=v)
    for u in range(6):
        if indeg[u] == 0:
            snap(7, u=u)
            q.append(u)
            snap(8, new=u)
    while front < len(q):
        snap(9)
        u = q[front]
        front += 1
        snap(10, u=u)
        order.append(u)
        done.add(u)
        snap(11, u=u)
        for v in T_ADJ[u]:
            indeg[v] -= 1
            snap(13, u=u, edge=(u, v), upd=v)
            if indeg[v] == 0:
                q.append(v)
                snap(14, u=u, edge=(u, v), new=v)
    snap(9)
    snap(16)
    return fr


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    render(os.path.join(d, 'topo_sort.gif'), TOPO_CODE, topo_frames(),
           draw_topo)

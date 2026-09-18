import math
import os
import matplotlib
matplotlib.use('Agg')
from gif_common import (render, cell, ptrbox, label, canvas, line, arrow,
                        circle_node, PTR)

VIS_FC = '#c8e6c9'
NEW_FC = '#dcedc8'
GREY = '#dddddd'
CUR = PTR[2]
EDGE_C = PTR[4]
FRONT_C = PTR[0]
REAR_C = PTR[1]
SCAN_C = PTR[3]
UPD_C = PTR[0]

# ================= 无向图（BFS / DFS 共用） =================
ADJ = {0: [1, 2], 1: [0, 3], 2: [0, 4], 3: [1, 5], 4: [2], 5: [3]}
EDGES = [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5)]


def draw_graph(ax, xy, edges, r=0.34, vis=frozenset(), cur=None, edge=None,
               out=frozenset(), fill=VIS_FC):
    for a, b in edges:
        hl = edge is not None and {a, b} == set(edge)
        line(ax, xy[a][0], xy[a][1], xy[b][0], xy[b][1],
             color=EDGE_C if hl else '#888888', lw=4 if hl else 2)
    for v in xy:
        fc = fill if v in vis else (GREY if v in out else '#ffffff')
        circle_node(ax, xy[v][0], xy[v][1], v, r=r, fc=fc, lw=2)
    if cur is not None:
        ptrbox(ax, xy[cur][0] - r, xy[cur][1] - r, 2 * r, 2 * r, CUR,
               lw=3, pad=0.06)


# ================= 1. BFS =================
BFS_CODE = [
    "void bfs(int g[][N], int n, int s) {",
    "    int q[N], front = 0, rear = 0;",
    "    int vis[N] = {0};",
    "    q[rear++] = s;",
    "    vis[s] = 1;",
    "    while (front < rear) {",
    "        int u = q[front++];",
    "        for (int v = 0; v < n; v++) {",
    "            if (g[u][v] && !vis[v]) {",
    "                vis[v] = 1;",
    "                q[rear++] = v;",
    "            }",
    "        }",
    "    }",
    "}",
]

BFS_XY = {0: (4.9, 6.9), 1: (2.7, 5.3), 2: (7.1, 5.3),
          3: (2.1, 3.7), 4: (7.7, 3.7), 5: (2.1, 2.1)}
QW, QH, QX0, QY0 = 1.15, 0.85, 1.0, 0.45


def draw_bfs(ax, s):
    canvas(ax, (0.4, 9.2), (0.1, 7.7))
    draw_graph(ax, BFS_XY, EDGES, vis=s['vis'], cur=s.get('u'),
               edge=s.get('edge'))
    q = s['q']
    for k in range(7):
        v = q[k] if k < len(q) else ''
        done = k < s['front']
        fc = '#eeeeee' if done else (NEW_FC if s.get('new') == v and v != ''
                                     else '#f9f9f9')
        cell(ax, QX0 + k * QW, QY0, QW, QH, v, fc=fc, fs=15,
             tc='#aaaaaa' if done else 'black')
    if s['front'] < 7:
        ptrbox(ax, QX0 + s['front'] * QW, QY0, QW, QH, FRONT_C, pad=0.015)
    if s['rear'] < 7:
        ptrbox(ax, QX0 + s['rear'] * QW, QY0, QW, QH, REAR_C, pad=0.06)


def bfs_frames():
    q, front, vis, fr = [], 0, set(), []

    def snap(ln, **kw):
        st = dict(q=list(q), front=front, rear=len(q), vis=set(vis))
        st.update(kw)
        fr.append((ln, st))

    snap(2)
    snap(3)
    q.append(0)
    vis.add(0)
    snap(4, new=0)
    snap(5, new=0)
    snap(6)
    while front < len(q):
        u = q[front]
        front += 1
        snap(7, u=u)
        for v in ADJ[u]:
            snap(8, u=u, edge=(u, v))
            if v not in vis:
                vis.add(v)
                snap(9, u=u, edge=(u, v))
                snap(10, u=u, edge=(u, v), new=v)
                q.append(v)
                snap(11, u=u, edge=(u, v), new=v)
    snap(6)
    snap(15)
    return fr


# ================= 2. DFS =================
DFS_CODE = [
    "void dfs(int g[][N], int n, int u, int* vis) {",
    "    vis[u] = 1;",
    "    for (int v = 0; v < n; v++) {",
    "        if (g[u][v] && !vis[v]) {",
    "            dfs(g, n, v, vis);",
    "        }",
    "    }",
    "}",
]

DFS_XY = {0: (3.3, 7.0), 1: (1.6, 5.4), 2: (5.0, 5.4),
          3: (1.2, 3.8), 4: (5.4, 3.8), 5: (1.2, 2.2)}
SW, SH, SX0, SBASE = 1.7, 0.85, 7.0, 1.8


def draw_dfs(ax, s):
    canvas(ax, (0.3, 9.0), (0.0, 7.7))
    draw_graph(ax, DFS_XY, EDGES, r=0.32, vis=s['vis'], cur=s.get('u'),
               edge=s.get('edge'))
    st = s['stack']
    for i, v in enumerate(st):
        cell(ax, SX0, SBASE + i * SH, SW, SH, v, fs=14,
             fc='#f9f9f9' if i < len(st) - 1 else NEW_FC)
    if st:
        ptrbox(ax, SX0, SBASE + (len(st) - 1) * SH, SW, SH, CUR)
    for k in range(6):
        v = s['order'][k] if k < len(s['order']) else ''
        cell(ax, 0.7 + k * 1.0, 0.35, 1.0, 0.8, v, fs=13,
             fc=NEW_FC if v != '' else '#f9f9f9')


def dfs_frames():
    vis, stack, order, fr = set(), [], [], []

    def snap(ln, u=None, edge=None):
        fr.append((ln, dict(vis=set(vis), stack=list(stack),
                            order=list(order), u=u, edge=edge)))

    def rec(u):
        stack.append(u)
        snap(1, u=u)
        vis.add(u)
        order.append(u)
        snap(2, u=u)
        for v in ADJ[u]:
            snap(3, u=u, edge=(u, v))
            if v not in vis:
                snap(4, u=u, edge=(u, v))
                snap(5, u=u, edge=(u, v))
                rec(v)
            else:
                snap(4, u=u, edge=(u, v))
        snap(7, u=u)
        stack.pop()
        snap(8)

    rec(0)
    return fr


# ================= 3. Dijkstra =================
DIJ_CODE = [
    "void dijkstra(int g[][N], int n, int s) {",
    "    int dist[N], vis[N] = {0};",
    "    for (int i = 0; i < n; i++) dist[i] = INF;",
    "    dist[s] = 0;",
    "    for (int k = 0; k < n; k++) {",
    "        int u = -1;",
    "        for (int i = 0; i < n; i++)",
    "            if (!vis[i] && (u == -1 || dist[i] < dist[u]))",
    "                u = i;",
    "        vis[u] = 1;",
    "        for (int v = 0; v < n; v++)",
    "            if (g[u][v] < INF && dist[u] + g[u][v] < dist[v])",
    "                dist[v] = dist[u] + g[u][v];",
    "    }",
    "}",
]

DIJ_XY = {0: (1.1, 4.3), 1: (4.1, 6.3), 2: (4.1, 2.7),
          3: (7.7, 4.7), 4: (10.3, 2.3)}
DIJ_E = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 5), (2, 3, 8), (3, 4, 3)]
DIJ_ADJ = {0: [(1, 4), (2, 1)], 1: [(3, 5)], 2: [(1, 2), (3, 8)],
           3: [(4, 3)], 4: []}
DIJ_PATH = [(0, 2), (2, 1), (1, 3), (3, 4)]
DIJ_LBL = {(0, 1): (-0.32, 0.30), (0, 2): (0.06, 0.38), (2, 1): (-0.40, 0.0),
           (1, 3): (0.16, 0.34), (2, 3): (-0.32, 0.30), (3, 4): (0.32, 0.28)}
RD = 0.4
TW, TH, TX0, TY0 = 1.35, 0.85, 2.3, 0.45


def draw_dij(ax, s):
    canvas(ax, (0.2, 11.4), (0.15, 7.35))
    path = s.get('path') or []
    for a, b, w in DIJ_E:
        x1, y1 = DIJ_XY[a]
        x2, y2 = DIJ_XY[b]
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        act = s.get('edge') == (a, b)
        on = (a, b) in path
        col = CUR if on else (EDGE_C if act else '#888888')
        arrow(ax, x1 + ux * RD, y1 + uy * RD, x2 - ux * RD, y2 - uy * RD,
              color=col, lw=4 if (act or on) else 1.8)
        ox, oy = DIJ_LBL[(a, b)]
        label(ax, (x1 + x2) / 2 + ox, (y1 + y2) / 2 + oy, w, fs=13,
              color=col if (act or on) else '#444444')
    for v in DIJ_XY:
        fc = VIS_FC if s['vis'][v] else '#ffffff'
        circle_node(ax, DIJ_XY[v][0], DIJ_XY[v][1], v, r=RD, fc=fc, lw=2)
    if s.get('u') is not None:
        x, y = DIJ_XY[s['u']]
        ptrbox(ax, x - RD, y - RD, 2 * RD, 2 * RD, CUR, lw=3, pad=0.06)
    for i in range(5):
        x = TX0 + i * TW
        fc = '#e8eaf6' if s['vis'][i] else '#f9f9f9'
        if s.get('upd') == i:
            fc = '#fff8e1'
        cell(ax, x, TY0, TW, TH, 'INF' if s['dist'][i] >= 999 else s['dist'][i],
             fc=fc, fs=14)
        label(ax, x + TW / 2, TY0 - 0.28, i, color='#999999', fs=9)
        if s.get('scan') == i:
            ptrbox(ax, x, TY0, TW, TH, SCAN_C)
        if s.get('upd') == i:
            ptrbox(ax, x, TY0, TW, TH, UPD_C)


def dijkstra_frames():
    n, INF = 5, 999
    dist, vis, fr = [INF] * n, [False] * n, []

    def snap(ln, **kw):
        st = dict(dist=list(dist), vis=list(vis))
        st.update(kw)
        fr.append((ln, st))

    snap(2)
    snap(3)
    dist[0] = 0
    snap(4, upd=0)
    for k in range(n):
        snap(5)
        snap(6)
        if k == 0:
            snap(7)
        u = -1
        for i in range(n):
            if vis[i]:
                continue
            if u == -1 or dist[i] < dist[u]:
                u = i
                snap(9, scan=i, u=u)
            else:
                snap(8, scan=i, u=u)
        vis[u] = True
        snap(10, u=u)
        if DIJ_ADJ[u]:
            snap(11, u=u)
        for v, w in DIJ_ADJ[u]:
            ok = dist[u] + w < dist[v]
            snap(12, u=u, edge=(u, v), ok=ok)
            if ok:
                dist[v] = dist[u] + w
                snap(13, u=u, edge=(u, v), upd=v)
    snap(14)
    snap(15, path=list(DIJ_PATH))
    return fr


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    render(os.path.join(d, 'graph_bfs.gif'), BFS_CODE, bfs_frames(), draw_bfs)
    render(os.path.join(d, 'graph_dfs.gif'), DFS_CODE, dfs_frames(), draw_dfs)
    render(os.path.join(d, 'dijkstra.gif'), DIJ_CODE, dijkstra_frames(),
           draw_dij)

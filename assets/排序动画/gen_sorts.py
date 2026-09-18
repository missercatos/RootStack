import os
from gif_common import render, cell, ptrbox, label, canvas, rect, PTR

W, H = 1.0, 0.95
BASE = 0.95
FILL, HOT = '#f9f9f9', '#fff8e1'
GREY = '#e0e4e8'
GREEN_T, RED_T = '#c8e6c9', '#ffcdd2'


# ---------------- 冒泡排序 ----------------
BUBBLE_CODE = [
    "void bubble_sort(int* a, int n) {",
    "    for (int i = 0; i < n - 1; i++) {",
    "        for (int j = 0; j < n - 1 - i; j++) {",
    "            if (a[j] > a[j + 1]) {",
    "                int t = a[j];",
    "                a[j] = a[j + 1];",
    "                a[j + 1] = t;",
    "            }",
    "        }",
    "    }",
    "}",
]
BUBBLE_A = [5, 3, 8, 4, 2]


def draw_bubble(ax, s):
    a = s['a']
    n = len(a)
    canvas(ax, (-1.0, n * W + 1.0), (-1.0, 2.6))
    sf = s.get('sorted_from', n)
    if sf < n:
        rect(ax, sf * W - 0.04, BASE - 0.04, (n - sf) * W + 0.08, H + 0.08,
             fc='#eceff1', ec='none')
    for k in range(n):
        fc = GREY if k >= sf else FILL
        if s.get('hot') == k:
            fc = HOT
        cell(ax, k * W, BASE, W, H, a[k], fc=fc, fs=14)
        label(ax, k * W + W / 2, BASE - 0.32, str(k), color='#999999', fs=9)
    j = s.get('j')
    if j is not None:
        ptrbox(ax, j * W, BASE, W, H, PTR[0], pad=0.02)
        ptrbox(ax, (j + 1) * W, BASE, W, H, PTR[1], pad=0.02)


def gen_bubble(path):
    a = list(BUBBLE_A)
    n = len(a)
    frames = []

    def snap(line, **kw):
        st = dict(a=list(a), j=None, hot=None, sorted_from=n)
        st.update(kw)
        frames.append((line, st))

    snap(1)
    for i in range(n - 1):
        snap(2, sorted_from=n - i)
        for j in range(n - 1 - i):
            snap(4, j=j, sorted_from=n - i)
            if a[j] > a[j + 1]:
                t = a[j]
                snap(5, j=j, hot=j, sorted_from=n - i)
                a[j] = a[j + 1]
                snap(6, j=j, hot=j, sorted_from=n - i)
                a[j + 1] = t
                snap(7, j=j, hot=j + 1, sorted_from=n - i)
        snap(9, sorted_from=n - 1 - i)
    snap(2, sorted_from=0)
    snap(11, sorted_from=0)
    render(path, BUBBLE_CODE, frames, draw_bubble, interval=450)


# ---------------- 快速排序（Lomuto 分区） ----------------
QUICK_CODE = [
    "int partition(int* a, int l, int r) {",
    "    int pivot = a[r];",
    "    int i = l - 1;",
    "    for (int j = l; j < r; j++) {",
    "        if (a[j] <= pivot) {",
    "            i++;",
    "            int t = a[i];",
    "            a[i] = a[j];",
    "            a[j] = t;",
    "        }",
    "    }",
    "    int t = a[i + 1];",
    "    a[i + 1] = a[r];",
    "    a[r] = t;",
    "    return i + 1;",
    "}",
]
QUICK_A = [7, 2, 8, 4, 5]


def draw_quick(ax, s):
    a = s['a']
    n = len(a)
    canvas(ax, (-1.0, n * W + 1.0), (-1.0, 2.6))
    part = s.get('part')
    for k in range(n):
        fc = FILL
        if s.get('hot') == k:
            fc = HOT
        elif s.get('cmpcell') == k:
            fc = GREEN_T if s.get('cmpok') else RED_T
        elif part is not None and k < part:
            fc = '#e8f5e9'
        elif part is not None and k > part:
            fc = '#e3f2fd'
        elif part is not None and k == part:
            fc = '#ffe0b2'
        cell(ax, k * W, BASE, W, H, a[k], fc=fc, fs=14)
        label(ax, k * W + W / 2, BASE - 0.32, str(k), color='#999999', fs=9)
    if s.get('pp') is not None:
        ptrbox(ax, s['pp'] * W, BASE, W, H, PTR[2], pad=0.02)
    if s.get('ii') is not None:
        ptrbox(ax, s['ii'] * W, BASE, W, H, PTR[0], pad=0.02)
    if s.get('jj') is not None:
        ptrbox(ax, s['jj'] * W, BASE, W, H, PTR[1], pad=0.02)


def gen_quick(path):
    a = list(QUICK_A)
    n = len(a)
    r = n - 1
    pp, i = r, -1
    frames = []

    def snap(line, **kw):
        st = dict(a=list(a), pp=pp, ii=i if i >= 0 else None, jj=None,
                  hot=None, cmpcell=None, cmpok=None, part=None)
        st.update(kw)
        frames.append((line, st))

    snap(1)
    snap(2)
    snap(3)
    for j in range(r):
        snap(4, jj=j)
        if a[j] <= a[r]:
            snap(5, jj=j, cmpcell=j, cmpok=True)
            i += 1
            snap(6, jj=j)
            t = a[i]
            snap(7, jj=j, hot=i)
            a[i] = a[j]
            snap(8, jj=j, hot=i)
            a[j] = t
            snap(9, jj=j, hot=j)
        else:
            snap(5, jj=j, cmpcell=j, cmpok=False)
    t = a[i + 1]
    snap(12, hot=i + 1)
    a[i + 1] = a[r]
    pp = i + 1
    snap(13, hot=i + 1)
    a[r] = t
    snap(14, hot=r)
    snap(15, part=i + 1)
    render(path, QUICK_CODE, frames, draw_quick, interval=450)


# ---------------- 归并排序（合并步骤） ----------------
MERGE_CODE = [
    "void merge(int* a, int* t, int l, int m, int r) {",
    "    int i = l, j = m + 1, k = l;",
    "    while (i <= m && j <= r) {",
    "        if (a[i] <= a[j]) t[k++] = a[i++];",
    "        else t[k++] = a[j++];",
    "    }",
    "    while (i <= m) t[k++] = a[i++];",
    "    while (j <= r) t[k++] = a[j++];",
    "    for (i = l; i <= r; i++) a[i] = t[i];",
    "}",
]
MERGE_A = [1, 4, 7, 2, 3, 9]
GAP = 0.4
FILL_T = '#f2f7fc'


def mx(k):
    return k if k <= 2 else k + GAP


def draw_merge(ax, s):
    a, t = s['a'], s['t']
    n = len(a)
    canvas(ax, (-1.8, mx(n - 1) + W + 0.9), (-0.9, 3.2))
    ax.plot([mx(2) + W + GAP / 2] * 2, [-0.55, 2.95],
            color='#cfd8dc', lw=1.4, ls=(0, (4, 4)), zorder=0)
    label(ax, -0.65, 2.45, 'a', color='#888888', fs=12)
    label(ax, -0.65, 1.0, 't', color='#888888', fs=12)
    for k in range(n):
        x = mx(k)
        fc = HOT if s.get('hot_a') == k else FILL
        cell(ax, x, 2.0, W, H, a[k], fc=fc, fs=14)
        label(ax, x + W / 2, 1.68, str(k), color='#999999', fs=9)
        fc = HOT if s.get('hot_t') == k else FILL_T
        v = t[k]
        cell(ax, x, 0.55, W, H, '' if v is None else v, fc=fc, fs=14)
        label(ax, x + W / 2, 0.23, str(k), color='#999999', fs=9)
    for k, col in ((s.get('ii'), PTR[0]), (s.get('jj'), PTR[1])):
        if k is not None:
            ptrbox(ax, mx(k), 2.0, W, H, col, pad=0.02)
    if s.get('kk') is not None:
        ptrbox(ax, mx(s['kk']), 0.55, W, H, PTR[2], pad=0.02)


def gen_merge(path):
    a = list(MERGE_A)
    n = len(a)
    t = [None] * n
    l, m, r = 0, 2, 5
    i, j, k = l, m + 1, l
    frames = []

    def snap(line, **kw):
        st = dict(a=list(a), t=list(t),
                  ii=i if i <= m else None, jj=j if j <= r else None,
                  kk=k if k <= r else None, hot_a=None, hot_t=None)
        st.update(kw)
        frames.append((line, st))

    snap(1)
    snap(2)
    while i <= m and j <= r:
        snap(3)
        if a[i] <= a[j]:
            i0, j0, k0 = i, j, k
            t[k0] = a[i0]
            i, k = i + 1, k + 1
            snap(4, ii=i0, jj=j0, kk=k0, hot_a=i0, hot_t=k0)
        else:
            i0, j0, k0 = i, j, k
            t[k0] = a[j0]
            j, k = j + 1, k + 1
            snap(5, ii=i0, jj=j0, kk=k0, hot_a=j0, hot_t=k0)
    snap(7)
    while j <= r:
        j0, k0 = j, k
        t[k0] = a[j0]
        j, k = j + 1, k + 1
        snap(8, jj=j0, kk=k0, hot_a=j0, hot_t=k0)
    for idx in range(l, r + 1):
        a[idx] = t[idx]
        snap(9, ii=idx, jj=None, kk=None, hot_a=idx, hot_t=idx)
    render(path, MERGE_CODE, frames, draw_merge, interval=450)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen_bubble(os.path.join(d, 'bubble_sort.gif'))
    gen_quick(os.path.join(d, 'quick_sort_partition.gif'))
    gen_merge(os.path.join(d, 'merge_sort.gif'))

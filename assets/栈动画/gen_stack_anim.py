"""栈动画 GIF 生成脚本（生成后统一删除）"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as patches
from gif_common import (render, cell, label, canvas, PTR, YELLOW,
                        YELLOW_EDGE)

ORANGE = PTR[4]
NSLOT = 4


def hl(ax, x, y, w, h, color=YELLOW, ec=YELLOW_EDGE, alpha=0.8, z=2.5):
    ax.add_patch(patches.FancyBboxPatch(
        (x + 0.06, y + 0.06), w - 0.12, h - 0.12,
        boxstyle='round,pad=0.05', facecolor=color, edgecolor=ec,
        lw=3.0, alpha=alpha, zorder=z))


def curbox(ax, x, y, w, h):
    ax.add_patch(patches.FancyBboxPatch(
        (x + 0.03, y + 0.03), w - 0.06, h - 0.06,
        boxstyle='round,pad=0.06', facecolor='#ffe0b2', edgecolor=ORANGE,
        lw=3.4, alpha=0.95, zorder=2.6))


def slot(ax, x, y, w, h, fc='#f7f7f7', ec='#cccccc', lw=1.2):
    cell(ax, x, y, w, h, '', fc=fc, ec=ec, lw=lw)


def draw_stack(ax, x0, y0, w, h, vals, hlt=None, fs=16):
    for j in range(NSLOT):
        slot(ax, x0, y0 + j * h, w, h)
    for j, v in enumerate(vals):
        y = y0 + j * h
        cell(ax, x0, y, w, h, v, fc='#ffffff', ec='#555555', lw=1.9, fs=fs)
        if hlt == j:
            hl(ax, x0, y, w, h)


# ---------------------------------------------------------------- 括号匹配
BRACKET_CODE = [
    "int bracket_match(const char* s) {",
    "    char st[100];",
    "    int top = -1;",
    "    for (int i = 0; s[i]; i++) {",
    "        if (s[i] == '(')",
    "            st[++top] = s[i];",
    "        else if (s[i] == ')') {",
    "            if (top == -1)",
    "                return 0;",
    "            top--;",
    "        }",
    "    }",
    "    return top == -1;",
    "}",
]
BS = '(()())'
BX0, BY, BW, BH = 1.8, 6.4, 2.1, 1.9
SSX, SSY, SSW, SSH = 15.8, 0.9, 2.6, 1.6


def draw_bracket(ax, st):
    canvas(ax, (-0.5, 20.5), (0.3, 9.6))
    for k, ch in enumerate(BS):
        cell(ax, BX0 + k * BW, BY, BW, BH, ch, fc='#ffffff', ec='#666666',
             lw=1.6, fs=16)
        label(ax, BX0 + k * BW + BW / 2, BY - 0.35, str(k),
              color='#999999', fs=10)
    if 0 <= st['i'] < len(BS):
        curbox(ax, BX0 + st['i'] * BW, BY, BW, BH)
    draw_stack(ax, SSX, SSY, SSW, SSH, st['stack'], st['hl'])
    ax.plot([SSX - 0.15, SSX + SSW + 0.15], [SSY, SSY], color='#888888',
            lw=2.0, zorder=1)


def gen_bracket(path):
    st = []
    frames = [(1, dict(i=-1, stack=[], hl=None)),
              (3, dict(i=-1, stack=[], hl=None))]
    for i, ch in enumerate(BS):
        frames.append((4, dict(i=i, stack=list(st), hl=None)))
        if ch == '(':
            frames.append((5, dict(i=i, stack=list(st), hl=None)))
            st.append(ch)
            frames.append((6, dict(i=i, stack=list(st), hl=len(st) - 1)))
        else:
            frames.append((7, dict(i=i, stack=list(st), hl=None)))
            frames.append((8, dict(i=i, stack=list(st), hl=None)))
            frames.append((10, dict(i=i, stack=list(st), hl=len(st) - 1)))
            st.pop()
    frames.append((4, dict(i=len(BS), stack=list(st), hl=None)))
    frames.append((13, dict(i=len(BS), stack=list(st), hl=None)))
    render(path, BRACKET_CODE, frames, draw_bracket, interval=500)


# ---------------------------------------------------------------- 中缀转后缀
INFIX_CODE = [
    "void infix_to_postfix(const char* s, char* out) {",
    "    char st[100]; int top = -1, k = 0;",
    "    for (int i = 0; s[i]; i++) {",
    "        char c = s[i];",
    "        if (c >= '0' && c <= '9')",
    "            out[k++] = c;",
    "        else {",
    "            while (top >= 0 && prec(st[top]) >= prec(c))",
    "                out[k++] = st[top--];",
    "            st[++top] = c;",
    "        }",
    "    }",
    "    while (top >= 0) out[k++] = st[top--];",
    "    out[k] = 0;",
    "}",
]
EXPR = '3+4*2-1'
PREC = {'+': 1, '-': 1, '*': 2, '/': 2}
FX0, FY, FW, FH = 1.4, 7.7, 1.9, 1.7
OX0, OY, OW, OH = 1.4, 5.1, 1.9, 1.7
ISX, ISY, ISW, ISH = 16.2, 0.9, 2.8, 1.6


def draw_infix(ax, st):
    canvas(ax, (-0.5, 20.5), (0.3, 10.0))
    for k, ch in enumerate(EXPR):
        cell(ax, FX0 + k * FW, FY, FW, FH, ch, fc='#ffffff', ec='#666666',
             lw=1.6, fs=16)
        label(ax, FX0 + k * FW + FW / 2, FY - 0.35, str(k),
              color='#999999', fs=10)
    if 0 <= st['i'] < len(EXPR):
        curbox(ax, FX0 + st['i'] * FW, FY, FW, FH)
    for k in range(len(EXPR)):
        x = OX0 + k * OW
        if k < len(st['out']):
            cell(ax, x, OY, OW, OH, st['out'][k], fc='#ffffff',
                 ec='#555555', lw=1.7, fs=16)
            if st['ho'] == k:
                hl(ax, x, OY, OW, OH)
        else:
            slot(ax, x, OY, OW, OH)
    draw_stack(ax, ISX, ISY, ISW, ISH, st['stack'], st['hs'])
    ax.plot([ISX - 0.15, ISX + ISW + 0.15], [ISY, ISY], color='#888888',
            lw=2.0, zorder=1)


def ib(i, out, stack, ho=None, hs=None):
    return dict(i=i, out=list(out), stack=list(stack), ho=ho, hs=hs)


def gen_infix(path):
    out, stk = [], []
    frames = [(1, ib(-1, out, stk))]
    for i, ch in enumerate(EXPR):
        frames.append((4, ib(i, out, stk)))
        if ch.isdigit():
            frames.append((5, ib(i, out, stk)))
            out.append(ch)
            frames.append((6, ib(i, out, stk, ho=len(out) - 1)))
        else:
            frames.append((7, ib(i, out, stk)))
            while stk and PREC[stk[-1]] >= PREC[ch]:
                frames.append((8, ib(i, out, stk, hs=len(stk) - 1)))
                out.append(stk.pop())
                frames.append((9, ib(i, out, stk, ho=len(out) - 1)))
            frames.append((8, ib(i, out, stk)))
            stk.append(ch)
            frames.append((10, ib(i, out, stk, hs=len(stk) - 1)))
    while stk:
        frames.append((13, ib(len(EXPR), out, stk, hs=len(stk) - 1)))
        out.append(stk.pop())
        frames.append((13, ib(len(EXPR), out, stk, ho=len(out) - 1)))
    frames.append((14, ib(len(EXPR), out, stk)))
    render(path, INFIX_CODE, frames, draw_infix, interval=500)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    gen_bracket(os.path.join(d, 'bracket_match.gif'))
    gen_infix(os.path.join(d, 'infix_to_postfix.gif'))

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation

# ---------- Data ----------
a = "ABC"
b = "AC"
n, m = len(a), len(b)

# ---------- Core source code (no comments) ----------
code_lines = [
    "int lcs(const char* a, int n, const char* b, int m) {",
    "    int* dp = malloc((m + 1) * sizeof(int));",
    "    for (int j = 0; j <= m; j++) dp[j] = 0;",
    "    for (int i = 1; i <= n; i++) {",
    "        int diag = dp[0];",
    "        for (int j = 1; j <= m; j++) {",
    "            int up = dp[j];",
    "            if (a[i-1] == b[j-1])",
    "                dp[j] = diag + 1;",
    "            else",
    "                dp[j] = dp[j-1] > up ? dp[j-1] : up;",
    "            diag = up;",
    "        }",
    "    }",
    "    int ans = dp[m]; free(dp); return ans;",
    "}"
]

# ---------- Simulate LCS and record all rows ----------
def simulate_lcs():
    all_rows = []
    phases = []
    dp = [0] * (m + 1)
    # row 0
    all_rows.append(dp[:])
    phases.append((3, 0, 0, all_rows[:], []))   # after init

    for i in range(1, n + 1):
        diag = dp[0]
        # inner loop
        for j in range(1, m + 1):
            up = dp[j]
            # record state before update (with highlights for dependencies)
            phases.append((8, i, j, all_rows[:] + [dp[:]], [('up', j), ('diag', j-1)]))
            if a[i-1] == b[j-1]:
                dp[j] = diag + 1
                phases.append((10, i, j, all_rows[:] + [dp[:]], [('current', j), ('diag', j-1)]))
            else:
                dp[j] = dp[j-1] if dp[j-1] > up else up
                phases.append((12, i, j, all_rows[:] + [dp[:]], [('current', j), ('left', j-1), ('up', j)]))
            diag = up
            phases.append((13, i, j, all_rows[:] + [dp[:]], []))
        # after finishing row i, save the full row
        all_rows.append(dp[:])
        if i < n:
            phases.append((5, i, 0, all_rows[:], []))   # next outer loop
    phases.append((15, n+1, m, all_rows[:], []))   # return
    return phases

phases = simulate_lcs()
hold_frames = 6
interval = 800

def build_frames(phases):
    frames = []
    for line, i, j, dp_rows, highlights in phases:
        frames.append((line, i, j, dp_rows, highlights))
    return frames

base_frames = build_frames(phases)
final_frame = base_frames[-1]
extended_frames = base_frames + [final_frame] * hold_frames

# ---------- Plot ----------
fig, (ax_code, ax_arr) = plt.subplots(2, 1, figsize=(12, 9),
                                       gridspec_kw={'height_ratios': [1.5, 2.2]})
ax_code.set_facecolor('#f8f9fa')
ax_arr.set_facecolor('#fafafa')

line_gap = 1.8   # code line spacing

def draw_frame(frame):
    line_num, i, j, dp_rows, highlights = frame

    # ---- Code area ----
    ax_code.clear()
    ax_code.set_xlim(0, 1)
    ax_code.set_ylim(0, len(code_lines) * line_gap + 0.8)
    ax_code.axis('off')
    for idx, txt in enumerate(code_lines):
        y = (len(code_lines) - idx - 0.5) * line_gap
        if idx + 1 == line_num:
            bbox_props = dict(boxstyle="round,pad=0.02", facecolor='#ffeb3b',
                              edgecolor='#fbc02d', linewidth=1.5)
            fontweight = 'bold'
        else:
            bbox_props = None
            fontweight = 'normal'
        ax_code.text(0.05, y, txt, va='center', fontsize=11, family='monospace',
                     bbox=bbox_props, fontweight=fontweight)

    # ---- DP table area ----
    ax_arr.clear()
    current_i = len(dp_rows) - 1
    cell_w, cell_h = 1.0, 0.8

    ax_arr.set_xlim(-1.2, (m + 1) * cell_w + 0.8)
    ax_arr.set_ylim(-1.0, (current_i + 1) * cell_h + 0.8)
    ax_arr.set_aspect('equal')

    # Draw all cells
    for row_idx in range(current_i + 1):
        row_data = dp_rows[row_idx]
        y_base = (current_i - row_idx) * cell_h
        for col_idx in range(m + 1):
            val = row_data[col_idx]
            x = col_idx * cell_w
            rect = patches.Rectangle((x, y_base), cell_w, cell_h,
                                     linewidth=1.2, edgecolor='#aaaaaa',
                                     facecolor='#f9f9f9')
            ax_arr.add_patch(rect)
            ax_arr.text(x + cell_w/2, y_base + cell_h/2, str(val),
                        ha='center', va='center', fontsize=13, fontweight='bold')

    # Highlight boxes
    for typ, pos in highlights:
        if typ == 'current':
            y_base = 0.0
            x = pos * cell_w
            box = patches.FancyBboxPatch((x, y_base), cell_w, cell_h,
                                         boxstyle="round,pad=0.02",
                                         linewidth=4, edgecolor='#e74c3c',
                                         facecolor='#fadbd8', alpha=0.8)
            ax_arr.add_patch(box)
        elif typ == 'diag':
            if current_i > 0:
                y_base = cell_h
                x = pos * cell_w
                box = patches.FancyBboxPatch((x, y_base), cell_w, cell_h,
                                             boxstyle="round,pad=0.02",
                                             linewidth=3, edgecolor='#2ecc71',
                                             facecolor='#a9dfbf', alpha=0.6)
                ax_arr.add_patch(box)
        elif typ == 'up':
            if current_i > 0:
                y_base = cell_h
                x = pos * cell_w
                box = patches.FancyBboxPatch((x, y_base), cell_w, cell_h,
                                             boxstyle="round,pad=0.02",
                                             linewidth=3, edgecolor='#3498db',
                                             facecolor='#d6eaf8', alpha=0.6)
                ax_arr.add_patch(box)
        elif typ == 'left':
            y_base = 0.0
            x = pos * cell_w
            box = patches.FancyBboxPatch((x, y_base), cell_w, cell_h,
                                         boxstyle="round,pad=0.02",
                                         linewidth=3, edgecolor='#9b59b6',
                                         facecolor='#e8daef', alpha=0.6)
            ax_arr.add_patch(box)

    # Row labels: characters of a
    for row_idx in range(1, current_i + 1):
        if row_idx <= n:
            ch = a[row_idx - 1]
            y_base = (current_i - row_idx) * cell_h
            ax_arr.text(-0.6, y_base + cell_h/2, ch, ha='center', va='center',
                        fontsize=14, fontweight='bold')
    # Column labels: characters of b
    for col_idx in range(1, m + 1):
        ch = b[col_idx - 1]
        x = col_idx * cell_w + cell_w/2
        ax_arr.text(x, -0.6, ch, ha='center', va='center', fontsize=14, fontweight='bold')
    # Row/col indices
    for row_idx in range(current_i + 1):
        y_base = (current_i - row_idx) * cell_h
        ax_arr.text(-1.0, y_base + cell_h/2, str(row_idx), ha='center', va='center',
                    fontsize=9, color='#888')
    for col_idx in range(m + 1):
        x = col_idx * cell_w + cell_w/2
        ax_arr.text(x, -1.0, str(col_idx), ha='center', va='center',
                    fontsize=9, color='#888')

    # Legend (English)
    legend_items = [
        ('red', 'current'),
        ('green', 'diag'),
        ('blue', 'up'),
        ('purple', 'left')
    ]
    leg_x = (m + 1) * cell_w + 0.2
    leg_y = (current_i + 1) * cell_h - 0.3
    for idx, (color, label) in enumerate(legend_items):
        y = leg_y - idx * 0.5
        rect = patches.Rectangle((leg_x, y), 0.2, 0.2, facecolor=color, edgecolor='black', linewidth=1)
        ax_arr.add_patch(rect)
        ax_arr.text(leg_x + 0.3, y + 0.1, label, ha='left', va='center', fontsize=8, color='black')

    # Highlight final answer (last cell)
    if line_num == 15:
        x = m * cell_w
        y_base = (current_i - n) * cell_h
        box = patches.Rectangle((x, y_base), cell_w, cell_h,
                                linewidth=4, edgecolor='#2ecc71',
                                facecolor='none', linestyle='--')
        ax_arr.add_patch(box)

    ax_arr.axis('off')

# ---------- Generate GIF ----------
ani = FuncAnimation(fig, draw_frame, frames=extended_frames,
                    repeat=True, interval=interval)
ani.save('lcs.gif', writer='pillow', fps=1000/interval, dpi=120)
print("LCS animation saved as lcs.gif")

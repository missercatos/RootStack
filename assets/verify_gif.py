"""GIF 动画验证脚本（生成后删除）
用法: python3 verify_gif.py <gif 文件> [最少帧数]
检查: 帧数、尺寸、黄色高亮是否存在、下方动画区是否有内容、帧间是否有变化。
"""
import sys
from PIL import Image


def is_yellow(px):
    r, g, b = px[:3]
    return r > 225 and g > 195 and b < 130


def verify(path, min_frames=2):
    im = Image.open(path)
    frames = getattr(im, 'n_frames', 1)
    w, h = im.size
    yellow_frames = 0
    anim_frames = 0
    signatures = set()
    for idx in range(frames):
        im.seek(idx)
        rgb = im.convert('RGB')
        small = rgb.resize((w // 4, h // 4))
        top = small.crop((0, 0, w // 4, int(h // 4 * 0.45)))
        bot = small.crop((0, int(h // 4 * 0.45), w // 4, h // 4))
        top_px = list(top.getdata())
        bot_px = list(bot.getdata())
        if any(is_yellow(p) for p in top_px):
            yellow_frames += 1
        nonwhite = sum(1 for p in bot_px if p[0] < 245 or p[1] < 245 or p[2] < 245)
        if nonwhite > len(bot_px) * 0.005:
            anim_frames += 1
        signatures.add(hash(tuple(p for p in bot_px[::97])))
    ok = (frames >= min_frames and w >= 800 and h >= 600
          and yellow_frames >= min(frames, min_frames) and anim_frames >= min_frames
          and len(signatures) >= 2)
    print(f"{path}: size={w}x{h} frames={frames} yellow_frames={yellow_frames} "
          f"anim_frames={anim_frames} distinct_states={len(signatures)} -> "
          f"{'PASS' if ok else 'FAIL'}")
    return ok


if __name__ == '__main__':
    p = sys.argv[1]
    mf = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    sys.exit(0 if verify(p, mf) else 1)

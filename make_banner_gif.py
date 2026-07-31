from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random

W, H = 700, 260
SCALE = 2
SW, SH = W * SCALE, H * SCALE
FPS = 24
DURATION = int(1000 / FPS)

BG = (8, 8, 8, 255)            # near-black like avatar
PANEL = (16, 16, 15, 255)
ACCENT = (227, 216, 212)        # warm off-white from avatar
ACCENT_DIM = (110, 105, 102)
TEXT = (232, 224, 219)
MUT = (90, 87, 84)
WARM = (233, 213, 204)

NAME_FONT = r"C:\Windows\Fonts\seguisb.ttf"
MONO_FONT = r"C:\Windows\Fonts\consolab.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def clamp255(v):
    return max(0, min(255, int(v)))

def lerp_color(c1, c2, t):
    return tuple(clamp255(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def render_name(img, t):
    letters = "FARMA"
    f = font(NAME_FONT, int(64 * SCALE))
    base_x = 116 * SCALE
    base_y = 88 * SCALE
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    pulse = 0.16 + 0.20 * math.sin(t * 2.2)
    gd.text((base_x, base_y), letters, font=f, fill=ACCENT + (int(255 * pulse),))
    glow = glow.filter(ImageFilter.GaussianBlur(12 * SCALE))
    img.alpha_composite(glow)

    d = ImageDraw.Draw(img)
    x = base_x
    for i, ch in enumerate(letters):
        phase = ((t - i * 0.32) % 3.0) / 3.0
        yoff = 0
        if phase < 0.14:
            yoff = -int(16 * SCALE * math.sin((phase / 0.14) * math.pi))
        c = lerp_color(WARM, ACCENT, (math.sin(t * 0.5 + i) + 1) / 2)
        d.text((x, base_y + 3 * SCALE + yoff), ch, font=f, fill=(0, 0, 0, 200))
        d.text((x, base_y + yoff), ch, font=f, fill=c)
        x += d.textlength(ch, font=f) + 6 * SCALE

def draw_bg(img, t):
    d = ImageDraw.Draw(img)
    for gy in range(SH):
        f = gy / SH
        base = lerp_color((8, 8, 8), (13, 13, 12), f)
        d.line([0, gy, SW, gy], fill=base)

def draw_grid(img, t):
    g = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    step = 28 * SCALE
    offset = int((t * 14 * SCALE) % step)
    for gx in range(0, SW, step):
        d.line([gx, 0, gx, SH], fill=ACCENT + (5,))
    for gy in range(-step, SH + step, step):
        d.line([0, gy + offset, SW, gy + offset], fill=ACCENT + (5,))
    img.alpha_composite(g)

def draw_frame(img, t, emoji_frames):
    d = ImageDraw.Draw(img)

    d.rounded_rectangle([10 * SCALE, 10 * SCALE, SW - 10 * SCALE, SH - 10 * SCALE],
                        radius=6 * SCALE, outline=(36, 36, 34, 255), width=2 * SCALE)
    cb = 22 * SCALE
    for cx, cy, sx, sy in [(10 * SCALE, 10 * SCALE, 1, 1),
                           (SW - 10 * SCALE, 10 * SCALE, -1, 1),
                           (SW - 10 * SCALE, SH - 10 * SCALE, -1, -1),
                           (10 * SCALE, SH - 10 * SCALE, 1, -1)]:
        d.line([cx, cy, cx + cb * sx, cy], fill=ACCENT, width=2 * SCALE)
        d.line([cx, cy, cx, cy + cb * sy], fill=ACCENT, width=2 * SCALE)

    mf = font(MONO_FONT, int(11 * SCALE))
    d.text((24 * SCALE, 30 * SCALE), "Farma@profile:~$ ./launch boostUP", font=mf, fill=MUT)
    if int(t * 2) % 2 == 0:
        d.ellipse([618 * SCALE, 27 * SCALE, 630 * SCALE, 39 * SCALE], fill=ACCENT)

    # top-right LEDs in warm-grey tones
    for i in range(3):
        lx = SW - 34 * SCALE - i * 16 * SCALE
        on = int(t * 3 + i) % 3 == 0
        d.ellipse([lx, 28 * SCALE, lx + 8 * SCALE, 36 * SCALE],
                  fill=ACCENT if on else (44, 43, 41))

    render_name(img, t)

    sf = font(NAME_FONT, int(13 * SCALE))
    d.text((120 * SCALE, 178 * SCALE), "Desktop Apps  \u00b7  Discord Bots", font=sf, fill=TEXT)

    fi = int(t * 10) % len(emoji_frames)
    em = emoji_frames[fi].resize((int(54 * SCALE), int(54 * SCALE)), Image.LANCZOS)
    img.paste(em, (505 * SCALE, 92 * SCALE), em)

    pw = 430 * SCALE
    px, py = 24 * SCALE, 224 * SCALE
    d.rounded_rectangle([px, py, px + pw, py + 10 * SCALE], radius=5 * SCALE, fill=(26, 26, 24, 255))
    prog = min(1.0, ((t * 0.45) % 1.0))
    w = pw * prog
    d.rounded_rectangle([px, py, px + w, py + 10 * SCALE], radius=5 * SCALE, fill=ACCENT)
    sheen_x = px + ((t * 1.6 * pw) % (pw + 40 * SCALE)) - 20 * SCALE
    d.rounded_rectangle([sheen_x, py, sheen_x + 34 * SCALE, py + 10 * SCALE], radius=5 * SCALE,
                        fill=(255, 250, 245, 130))
    pct = int(prog * 100)
    d.text((px + pw + 14 * SCALE, py - 2 * SCALE), f"{pct}%", font=mf, fill=ACCENT)

    lines = [
        "\u279c  core modules ready",
        "\u279c  loading optimizations...",
        "[ OK ]  profile initialized",
    ]
    for li, ln in enumerate(lines):
        appear_at = li * 0.85
        local_t = (t - appear_at)
        if local_t < 0:
            continue
        nch = min(len(ln), int(local_t * 26))
        shown = ln[:nch]
        y = 190 * SCALE + li * 18 * SCALE
        col = WARM if ln.startswith("\u279c") else ACCENT
        d.text((24 * SCALE, y), shown, font=mf, fill=col)
        if nch < len(ln) and int(t * 3) % 2 == 0:
            d.text((24 * SCALE + d.textlength(shown, font=mf), y), "_", font=mf, fill=col)

    sy = int(((t * 150 * SCALE) % (SH + 200 * SCALE)) - 100 * SCALE)
    scan = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    h = 70 * SCALE
    for i in range(h):
        a = int(9 * math.exp(-i / (h * 0.3)))
        sd.line([12 * SCALE, sy + i, SW - 12 * SCALE, sy + i], fill=ACCENT + (a,))
    img.alpha_composite(scan)

    prng = random.Random(7)
    for i in range(22):
        pp = (prng.random() * SW, ((prng.random() * SH) - (t * 16 * SCALE) % SH) % SH)
        a = int(24 + 40 * math.sin(t * 2 + i))
        d.rectangle([pp[0], pp[1], pp[0] + SCALE, pp[1] + SCALE], fill=ACCENT + (a,))

    d.text((24 * SCALE, 246 * SCALE), "Farma@profile:~$", font=mf, fill=MUT)
    if int(t * 2.4) % 2 == 0:
        d.text((24 * SCALE + d.textlength("Farma@profile:~$", font=mf), 246 * SCALE), "_", font=mf, fill=ACCENT)

def main():
    emoji = Image.open(r"C:\Users\RAMZI\AppData\Local\Temp\opencode\farma3334\assets\emoji_anim.webp")
    emoji_frames = []
    for f in range(emoji.n_frames):
        emoji.seek(f)
        emoji_frames.append(emoji.copy().convert("RGBA"))
    if len(emoji_frames) == 1:
        emoji_frames = emoji_frames * 3

    total = int(4.5 * FPS)
    frames = []
    for i in range(total):
        t = i / FPS
        img = Image.new("RGBA", (SW, SH), BG)
        draw_bg(img, t)
        draw_grid(img, t)
        draw_frame(img, t, emoji_frames)
        down = img.resize((W, H), Image.LANCZOS).convert("P", palette=Image.ADAPTIVE, colors=255)
        frames.append(down)

    out = r"C:\Users\RAMZI\AppData\Local\Temp\opencode\farma3334\farma-banner.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=DURATION, loop=0, optimize=True)
    print("wrote", out, "frames:", len(frames))

if __name__ == "__main__":
    main()

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random

W, H = 700, 260
SCALE = 2
SW, SH = W * SCALE, H * SCALE
FPS = 24
DURATION = int(1000 / FPS)

BG = (7, 8, 13, 255)
GREEN = (0, 255, 157)
CYAN = (0, 229, 255)
DIM = (110, 118, 135)
TEXT = (214, 218, 228)
RED = (255, 77, 109)
YELLOW = (255, 209, 102)
PURPLE = (187, 134, 252)

NAME_FONT = r"C:\Windows\Fonts\seguisb.ttf"
MONO_FONT = r"C:\Windows\Fonts\consolab.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def clamp255(v):
    return max(0, min(255, int(v)))

def lerp_color(c1, c2, t):
    return tuple(clamp255(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def draw_gradient_text(d, x, y, text, font, c1, c2, shadow=None):
    if shadow:
        d.text((x + 3, y + 3), text, font=font, fill=shadow)
    total_w = d.textlength(text, font=font)
    for i, ch in enumerate(text):
        cw = d.textlength(ch, font=font)
        cx = x + d.textlength(text[:i], font=font)
        d.text((cx, y), ch, font=font, fill=c1)
    d.text((x, y), text, font=font, fill=c1)
    # gradient overlay via mask
    mask = Image.new("L", (int(total_w) + 4, int(font.size) + 4), 0)
    md = ImageDraw.Draw(mask)
    md.text((0, 0), text, font=font, fill=255)
    grad = Image.new("RGBA", (int(total_w) + 4, int(font.size) + 4))
    pg = grad.load()
    for gx in range(grad.width):
        t = gx / max(1, grad.width - 1)
        col = lerp_color(c1, c2, t)
        for gy in range(grad.height):
            pg[gx, gy] = col + (255,)
    # composite gradient onto canvas clipped by mask
    region = img_region = None
    # helper to composite: create layer
    return (text, x, y, font, grad, mask, int(total_w) + 4, int(font.size) + 4)

def apply_gradient(img, spec):
    text, x, y, f, grad, mask, gw, gh = spec
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.paste(grad, (int(x) - 2, int(y) - 2), mask)
    img.alpha_composite(layer)

def render_name(img, t):
    """Render FARMA with animated per-letter pop + hue travel + glow."""
    letters = "FARMA"
    f = font(NAME_FONT, int(64 * SCALE))
    base_x = 116 * SCALE
    base_y = 88 * SCALE
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    pulse = 0.18 + 0.22 * math.sin(t * 2.2)
    gd.text((base_x, base_y), letters, font=f, fill=(0, 255, 157, int(255 * pulse)))
    glow = glow.filter(ImageFilter.GaussianBlur(12 * SCALE))
    img.alpha_composite(glow)

    d = ImageDraw.Draw(img)
    x = base_x
    for i, ch in enumerate(letters):
        # pop cycle per letter, staggered
        phase = ((t - i * 0.32) % 3.0) / 3.0
        yoff = 0
        if phase < 0.14:
            yoff = -int(16 * SCALE * math.sin((phase / 0.14) * math.pi))
        hue_t = ((t * 0.12 + i * 0.2) % 1.0)
        c = lerp_color(GREEN, CYAN, hue_t)
        # draw letter twice: dark offset then bright for depth
        d.text((x, base_y + 3 * SCALE + yoff), ch, font=f, fill=(0, 0, 0, 160))
        d.text((x, base_y + yoff), ch, font=f, fill=c)
        x += d.textlength(ch, font=f) + 6 * SCALE
    return x

def draw_bg(img, t):
    d = ImageDraw.Draw(img)
    # dark vertical gradient
    for gy in range(SH):
        f = gy / SH
        c = int(lerp_color((7, 8, 13), (11, 13, 22), f)[0])
        d.line([0, gy, SW, gy], fill=(c, int(c * 1.1), int(c * 1.4)))

def draw_grid(img, t):
    g = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    step = 28 * SCALE
    offset = int((t * 14 * SCALE) % step)
    for gx in range(0, SW, step):
        d.line([gx, 0, gx, SH], fill=(0, 255, 157, 7))
    for gy in range(-step, SH + step, step):
        d.line([0, gy + offset, SW, gy + offset], fill=(0, 255, 157, 6))
    img.alpha_composite(g)

def draw_frame(img, t, emoji_frames):
    d = ImageDraw.Draw(img)

    # panel
    d.rounded_rectangle([10 * SCALE, 10 * SCALE, SW - 10 * SCALE, SH - 10 * SCALE],
                        radius=6 * SCALE, outline=(30, 34, 46, 255), width=2 * SCALE)
    # corner brackets
    cb = 22 * SCALE
    for cx, cy, sx, sy in [(10 * SCALE, 10 * SCALE, 1, 1),
                           (SW - 10 * SCALE, 10 * SCALE, -1, 1),
                           (SW - 10 * SCALE, SH - 10 * SCALE, -1, -1),
                           (10 * SCALE, SH - 10 * SCALE, 1, -1)]:
        d.line([cx, cy, cx + cb * sx, cy], fill=GREEN, width=2 * SCALE)
        d.line([cx, cy, cx, cy + cb * sy], fill=GREEN, width=2 * SCALE)

    # top-left status line with blinking dot
    mf = font(MONO_FONT, int(11 * SCALE))
    d.text((24 * SCALE, 30 * SCALE), "Farma@profile:~$ ./launch boostUP", font=mf, fill=DIM)
    if int(t * 2) % 2 == 0:
        d.ellipse([618 * SCALE, 27 * SCALE, 630 * SCALE, 39 * SCALE], fill=GREEN)

    # top-right LEDs
    for i, col in enumerate([RED, YELLOW, GREEN]):
        lx = SW - 34 * SCALE - i * 16 * SCALE
        on = int(t * 3 + i) % 3 == 0
        d.ellipse([lx, 28 * SCALE, lx + 8 * SCALE, 36 * SCALE], fill=col if on else (40, 42, 50))

    # FARMA name
    render_name(img, t)

    # subtitle
    sf = font(NAME_FONT, int(13 * SCALE))
    d.text((120 * SCALE, 178 * SCALE), "Desktop Apps  \u00b7  Discord Bots", font=sf, fill=TEXT)

    # emoji next to name
    fi = int(t * 10) % len(emoji_frames)
    em = emoji_frames[fi].resize((int(54 * SCALE), int(54 * SCALE)), Image.LANCZOS)
    img.paste(em, (505 * SCALE, 92 * SCALE), em)

    # progress bar with striped sheen + % label
    pw = 430 * SCALE
    px, py = 24 * SCALE, 224 * SCALE
    d.rounded_rectangle([px, py, px + pw, py + 10 * SCALE], radius=5 * SCALE, fill=(18, 20, 28, 255))
    prog = min(1.0, ((t * 0.45) % 1.0))
    w = pw * prog
    d.rounded_rectangle([px, py, px + w, py + 10 * SCALE], radius=5 * SCALE, fill=GREEN)
    # sheen
    sheen_x = px + ((t * 1.6 * pw) % (pw + 40 * SCALE)) - 20 * SCALE
    d.rounded_rectangle([sheen_x, py, sheen_x + 34 * SCALE, py + 10 * SCALE], radius=5 * SCALE,
                        fill=(255, 255, 255, 140))
    pct = int(prog * 100)
    d.text((px + pw + 14 * SCALE, py - 2 * SCALE), f"{pct}%", font=mf, fill=GREEN)

    # boot log with typing effect
    lines = [
        "\u279c  core modules ready",
        "\u279c  loading optimizations...",
        "[ OK ]  profile initialized",
    ]
    for li, ln in enumerate(lines):
        show_for = 1.2 + li * 0.5
        appear_at = li * 0.85
        local_t = (t - appear_at)
        if local_t < 0:
            continue
        nch = min(len(ln), int(local_t * 26))
        shown = ln[:nch]
        y = 190 * SCALE + li * 18 * SCALE
        col = CYAN if ln.startswith("\u279c") else GREEN
        d.text((24 * SCALE, y), shown, font=mf, fill=col)
        if nch < len(ln) and int(t * 3) % 2 == 0:
            d.text((24 * SCALE + d.textlength(shown, font=mf), y), "_", font=mf, fill=col)

    # scanline sweep
    sy = int(((t * 150 * SCALE) % (SH + 200 * SCALE)) - 100 * SCALE)
    scan = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    h = 70 * SCALE
    for i in range(h):
        a = int(10 * math.exp(-i / (h * 0.3)))
        sd.line([12 * SCALE, sy + i, SW - 12 * SCALE, sy + i], fill=(0, 255, 157, a))
    img.alpha_composite(scan)

    # particles
    prng = random.Random(7)
    for i in range(26):
        pp = (prng.random() * SW, ((prng.random() * SH) - (t * 18 * SCALE) % SH) % SH)
        a = int(30 + 50 * math.sin(t * 2 + i))
        d.rectangle([pp[0], pp[1], pp[0] + SCALE, pp[1] + SCALE], fill=(0, 255, 157, a))

    # bottom status line + cursor
    d.text((24 * SCALE, 246 * SCALE), "Farma@profile:~$", font=mf, fill=DIM)
    if int(t * 2.4) % 2 == 0:
        d.text((24 * SCALE + d.textlength("Farma@profile:~$", font=mf), 246 * SCALE), "_", font=mf, fill=GREEN)

def main():
    emoji = Image.open(r"C:\Users\RAMZI\AppData\Local\Temp\opencode\farma3334\assets\emoji_anim.webp")
    emoji_frames = []
    for f in range(emoji.n_frames):
        emoji.seek(f)
        emoji_frames.append(emoji.copy().convert("RGBA"))
    # make 2 static variants by mirroring for smoothness
    if len(emoji_frames) == 1:
        emoji_frames = emoji_frames * 3

    total = int(4.5 * FPS)  # 4.5s loop
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

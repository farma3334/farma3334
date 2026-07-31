from PIL import Image, ImageDraw, ImageFont
import math

W, H = 700, 260
FPS = 20
DURATION = int(1000 / FPS)
BG = (10, 10, 15, 255)
GREEN = (0, 255, 157, 255)
CYAN = (0, 229, 255, 255)
DIM = (85, 85, 95, 255)
TEXT = (208, 208, 216, 255)
FAINT_GREEN = (0, 255, 157, 15)

def font(size, bold=False):
    paths = [
        r"C:\Windows\Fonts\courbd.ttf" if bold else r"C:\Windows\Fonts\cour.ttf",
        r"C:\Windows\Fonts\consolab.ttf" if bold else r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\lucon.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

def lerp(a, b, t):
    return a + (b - a) * t

def hex_color(start, end, t):
    return tuple(int(lerp(start[i], end[i], t)) for i in range(3))

def draw_frame(t, emoji_frames):
    img = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(img)

    # outer frame + corner brackets
    d.rectangle([14, 14, W - 14, H - 14], outline=(10, 10, 15, 255), width=1)
    d.line([14, 14, W - 14, 14], fill=(26, 26, 34, 255))
    d.line([14, H - 14, W - 14, H - 14], fill=(26, 26, 34, 255))
    for cx, cy, sx, sy in [(14, 14, 1, 1), (W - 14, 14, -1, 1), (W - 14, H - 14, -1, -1), (14, H - 14, 1, -1)]:
        d.line([cx, cy, cx + 18 * sx, cy], fill=GREEN, width=2)
        d.line([cx, cy, cx, cy + 18 * sy], fill=GREEN, width=2)

    # top status line
    d.text((24, 32), "Farma@profile:~$ ./launch boostUP", font=font(12), fill=DIM)

    # progress bar
    pw = 440
    px, py = 24, 224
    d.rounded_rectangle([px, py, px + pw, py + 10], radius=5, fill=(16, 16, 22, 255))
    fill = min(1.0, (t % 3.6) / 3.6)
    d.rounded_rectangle([px, py, px + pw * fill, py + 10], radius=5, fill=GREEN)
    d.text((px + pw + 10, py - 1), f"{int(fill * 100)}%", font=font(12), fill=GREEN)

    # FARMA letters - staggered pop animation
    letters = "FARMA"
    x = 120
    f = font(74, bold=True)
    for i, ch in enumerate(letters):
        phase = ((t - i * 0.5) % 3.6) / 3.6
        yoff = 0
        if phase < 0.12:
            yoff = -int(14 * math.sin((phase / 0.12) * math.pi))
        c = hex_color((0, 255, 157), (0, 229, 255), (phase * 2) % 1)
        d.text((x, 92 + yoff), ch, font=f, fill=c + (255,))
        x += 72

    # glow pulse behind name
    pulse = 0.15 + 0.3 * (0.5 + 0.5 * math.sin(t * 2.4))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((120, 92), "FARMA", font=f, fill=(0, 255, 157, int(255 * pulse * 0.25)))
    img = Image.alpha_composite(img, glow)

    # subtitle
    d.text((120, 178), "Desktop Apps \u00b7 Discord Bots", font=font(13), fill=TEXT)

    # emoji (animated)
    fi = int(t * 8) % len(emoji_frames)
    img.paste(emoji_frames[fi], (498, 96), emoji_frames[fi])

    # scanline
    sy = int(((t * 130) % (H + 160)) - 80)
    scan = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    for i in range(90):
        sd.line([14, sy + i, W - 14, sy + i], fill=(0, 255, 157, int(8 * (1 - i / 90))))
    img = Image.alpha_composite(img, scan)

    # boot lines
    d.text((24, 196), "\u279c  core modules ready", font=font(12), fill=CYAN)
    d.text((24, 212), "[ OK ]  profile initialized", font=font(12), fill=GREEN)

    # blinking cursor
    if int(t * 2) % 2 == 0:
        d.text((24, 244), "Farma@profile:~$ _", font=font(12), fill=DIM)
    else:
        d.text((24, 244), "Farma@profile:~$", font=font(12), fill=DIM)

    return img

def main():
    emoji = Image.open(r"C:\Users\RAMZI\AppData\Local\Temp\opencode\farma3334\assets\emoji_anim.webp")
    emoji_frames = [f.convert("RGBA") for f in range(emoji.n_frames) for f in [emoji.seek(f) or emoji.copy()]]

    frames = []
    total = 144
    for i in range(total):
        frames.append(draw_frame(i / FPS, emoji_frames))

    out = r"C:\Users\RAMZI\AppData\Local\Temp\opencode\farma3334\farma-banner.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=DURATION, loop=0, optimize=True)
    print("wrote", out, "frames:", len(frames))

if __name__ == "__main__":
    main()

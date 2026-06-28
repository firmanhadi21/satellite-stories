#!/usr/bin/env python3
"""
COMPOSE THE X VIDEO: time-lapse + narration + burned-in captions.
Inputs (in this folder):
  urban_sprawl.mp4  - from gee_urban_sprawl_timelapse.py (render_local)
  narration.mp3     - ElevenLabs export of the narration (see X-sawah-video-production.md)
Output:
  sawah_video.mp4   - square, X-ready

Install:
    pip install "moviepy>=2.0" pillow numpy
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, vfx

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_VIDEO = os.path.join(HERE, "urban_sprawl.mp4")
NARRATION = os.path.join(HERE, "narration.mp3")
OUT = os.path.join(HERE, "sawah_video.mp4")

SIZE = 1080                      # square 1080x1080 (set H=1350 below for vertical)
W, H = SIZE, SIZE

# Timed captions (start_sec, text) — for muted viewers. End time = next start.
CAPTIONS = [
    (0.0,  "Dua puluh tahun lalu, ini sawah."),
    (4.5,  "Sekarang? Lihat sendiri."),
    (9.0,  "Hijau → abu-abu: sawah jadi perumahan."),
    (17.0, "Swasembada beras, tapi sawah jadi rumah & pabrik."),
    (26.0, "Saya memetakan sawah Jawa dari satelit."),
    (31.0, "Luas sawah menyusut — pelan tapi pasti."),
    (36.0, "Citra satelit, tiap tahun, gratis. Datanya tak bohong."),
]
END_CARD = "Mana buktinya?\nAda di citra satelit.\n@jalmiburung"

def _font(size):
    for p in ["DejaVuSans-Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/Library/Fonts/Arial.ttf"]:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()

def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

def caption_img(text, w, h, pos="bottom"):
    """Render caption as an RGBA image (transparent bg, white text + dark band)."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = _font(int(w / 22))
    lines = []
    for para in text.split("\n"):
        lines += _wrap(d, para, font, w * 0.86)
    lh = int(font.size * 1.35)
    block_h = lh * len(lines)
    y0 = (h - block_h) // 2 if pos == "center" else int(h * 0.82) - block_h
    # translucent band
    d.rectangle([0, y0 - 18, w, y0 + block_h + 18], fill=(0, 0, 0, 120))
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=font)
        d.text(((w - tw) / 2, y0 + i * lh), ln, font=font, fill=(255, 255, 255, 255),
               stroke_width=2, stroke_fill=(0, 0, 0, 255))
    return np.array(img)

def main():
    if not (os.path.exists(BASE_VIDEO) and os.path.exists(NARRATION)):
        raise SystemExit(f"Need {BASE_VIDEO} and {NARRATION} (see X-sawah-video-production.md)")

    audio = AudioFileClip(NARRATION)
    dur = audio.duration + 2.0          # +2s tail for the end card

    # base time-lapse -> square, looped/trimmed to narration length
    base = VideoFileClip(BASE_VIDEO).without_audio()
    base = base.with_effects([vfx.Resize(height=H)])
    if base.w > W:                       # center-crop to square
        base = base.with_effects([vfx.Crop(x_center=base.w / 2, width=W)])
    base = base.with_effects([vfx.Loop(duration=dur)]).with_duration(dur)

    layers = [base]

    # timed captions
    for i, (start, text) in enumerate(CAPTIONS):
        end = CAPTIONS[i + 1][0] if i + 1 < len(CAPTIONS) else audio.duration
        clip = (ImageClip(caption_img(text, W, H), transparent=True)
                .with_start(start).with_duration(max(0.5, end - start)))
        layers.append(clip)

    # end card (last 2s)
    end_clip = (ImageClip(caption_img(END_CARD, W, H, pos="center"), transparent=True)
                .with_start(audio.duration).with_duration(2.0))
    layers.append(end_clip)

    video = CompositeVideoClip(layers, size=(W, H)).with_audio(audio).with_duration(dur)
    video.write_videofile(OUT, fps=30, codec="libx264", audio_codec="aac")
    print("Wrote", OUT)

if __name__ == "__main__":
    main()

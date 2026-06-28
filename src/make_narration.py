#!/usr/bin/env python3
"""
GENERATE narration.mp3 via the ElevenLabs API (Indonesian, multilingual v2).
Writes social-media/narration.mp3 and copies it into remotion-sawah/public/.

Credentials (NOT hardcoded) — env vars win, else Credentials/elevenlabs.txt.
Supported file formats (any of):
  1. KEY=VALUE lines:
        ELEVENLABS_API_KEY=sk_xxx
        ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
  2. Two bare lines (the 20-char alphanumeric token is taken as the Voice ID):
        sk_xxx
        21m00Tcm4TlvDq8ikWAM
  3. A single bare line (API key only; voice falls back to the default below)

Install:  pip install "elevenlabs>=1.0"
Usage:
    python social-media/make_narration.py            # generate narration.mp3
    python social-media/make_narration.py --list      # list voices (to pick a Voice ID)
"""

import os
import sys
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "narration.mp3")
PUBLIC = os.path.join(HERE, "remotion-sawah", "public")
CRED = os.path.join(HERE, "..", "Credentials", "elevenlabs.txt")

DEFAULT_VOICE = "pNInz6obpgDQGcFmaJgB"   # "Adam" — used only if no Voice ID is found
MODEL = "eleven_multilingual_v2"

NARRATION = (
    "Sepuluh tahun lalu, ini sawah. "
    "Warna merah ini bangunan — terang dipantulkan radar Sentinel-1. Sekarang, lihat sendiri. "
    "Merahnya terus meluas: kota dan pabrik menggantikan sawah. "
    "Bagaimana saya tahu? Bukan dari katanya. Dari satelit radar. "
    "Tiap beberapa hari, Sentinel-1 memindai Bumi. Bukan foto — ia merekam pantulan gelombang mikro dari permukaan, dalam bentuk angka. Menembus awan, siang dan malam. "
    "Dari angka itu kita pisahkan: bangunan memantul kuat dan tetap terang; sawah justru berubah-ubah, ikut musim tanam. "
    "Itulah sidik jari sawah: tergenang saat tanam, menghijau saat tumbuh, lalu dipanen. Naik-turun itu yang kita kenali. "
    "Saya susun puluhan citra, latih model, lalu petakan seluruh Jawa: mana yang masih sawah, mana yang sudah hilang. "
    "Hasilnya, sawah Jawa musim tanam ini sekitar dua koma tiga juta hektar — lumbung padi kita. "
    "Tapi angkanya terus turun. Tiap tahun, ribuan hektar beralih fungsi. "
    "Pertanyaan untuk Anda: kalau sawah terus menyusut, dari mana kita makan di tahun 2045? "
    "Penduduk bertambah, lahan berkurang. Indonesia Emas, atau Indonesia Lapar?"
)

def load_creds():
    """Return (api_key, voice_id). Env vars take precedence over the file."""
    key = os.environ.get("ELEVENLABS_API_KEY")
    vid = os.environ.get("ELEVENLABS_VOICE_ID")

    if (not key or not vid) and os.path.exists(CRED):
        kv, bare = {}, []
        for line in open(CRED).read().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                kv[k.strip().upper()] = v.strip()
            else:
                bare.append(line)
        key = key or kv.get("ELEVENLABS_API_KEY") or kv.get("API_KEY") or kv.get("KEY")
        vid = vid or kv.get("ELEVENLABS_VOICE_ID") or kv.get("VOICE_ID") or kv.get("VOICE")
        # bare tokens: a 20-char alphanumeric token is the Voice ID; the other is the key
        tokens = []
        for b in bare:
            tokens += b.replace(",", " ").split()
        if not vid:
            vid = next((t for t in tokens if len(t) == 20 and t.isalnum()), None)
        if not key:
            key = next((t for t in tokens if t != vid), None)

    if not key:
        sys.exit("No API key found. Put it in Credentials/elevenlabs.txt or set ELEVENLABS_API_KEY.")
    return key, (vid or DEFAULT_VOICE)

def list_voices():
    from elevenlabs.client import ElevenLabs
    key, _ = load_creds()
    for v in ElevenLabs(api_key=key).voices.get_all().voices:
        labels = getattr(v, "labels", {}) or {}
        print(f"{v.voice_id}  {v.name:20s}  {labels.get('gender','')}/{labels.get('accent','')}")

def main():
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    key, voice_id = load_creds()
    print(f"Using voice_id: {voice_id}")
    client = ElevenLabs(api_key=key)

    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        model_id=MODEL,
        text=NARRATION,
        output_format="mp3_44100_128",
        voice_settings=VoiceSettings(
            stability=0.5, similarity_boost=0.75, style=0.3, use_speaker_boost=True),
    )
    with open(OUT, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)
    print("Wrote", OUT)

    os.makedirs(PUBLIC, exist_ok=True)
    shutil.copy(OUT, os.path.join(PUBLIC, "narration.mp3"))
    print("Copied to", os.path.join(PUBLIC, "narration.mp3"))

if __name__ == "__main__":
    if "--list" in sys.argv:
        list_voices()
    else:
        main()

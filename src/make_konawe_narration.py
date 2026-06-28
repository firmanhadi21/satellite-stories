#!/usr/bin/env python3
"""
narration_konawe.mp3 via ElevenLabs (Indonesian). Same creds logic as make_narration.py
(env ELEVENLABS_API_KEY / ELEVENLABS_VOICE_ID, or Credentials/elevenlabs.txt).
Auto-copies into remotion-sawah/public/.

Install:  pip install "elevenlabs>=1.0"
"""

import os
import sys
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "narration_konawe.mp3")
PUBLIC = os.path.join(HERE, "remotion-sawah", "public")
CRED = os.path.join(HERE, "..", "Credentials", "elevenlabs.txt")
DEFAULT_VOICE = "pNInz6obpgDQGcFmaJgB"
MODEL = "eleven_multilingual_v2"

NARRATION = (
    "Sepuluh tahun lalu, ini hutan. "
    "Sekarang? Lihat sendiri. "
    "Hijau berubah jadi cokelat — hutan dikupas menjadi tambang nikel. "
    "Bagaimana saya tahu? Bukan dari katanya. Dari satelit. "
    "Tiap tahun satelit mengukur kehijauan permukaan — sebuah indeks bernama NDVI. "
    "Hutan rapat nilainya tinggi; tanah terbuka, rendah. "
    "Ketika hutan dibuka untuk tambang, NDVI anjlok. Satelit mencatatnya, petak demi petak, tahun demi tahun. "
    "Saya petakan kehilangannya. Di blok ini saja, ribuan hektar hutan lenyap dalam sepuluh tahun. "
    "Kita bangga menjadi raja nikel dunia. "
    "Tapi pertanyaan untuk Anda: berapa hutan dan sungai yang kita korbankan untuk itu? "
    "Baterai mobil listrik menyala di sana — air dan hutan padam di sini. Kemajuan, untuk siapa?"
)

def load_creds():
    key = os.environ.get("ELEVENLABS_API_KEY")
    vid = os.environ.get("ELEVENLABS_VOICE_ID")
    if (not key or not vid) and os.path.exists(CRED):
        kv, bare = {}, []
        for line in open(CRED).read().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1); kv[k.strip().upper()] = v.strip()
            else:
                bare.append(line)
        key = key or kv.get("ELEVENLABS_API_KEY") or kv.get("API_KEY") or kv.get("KEY")
        vid = vid or kv.get("ELEVENLABS_VOICE_ID") or kv.get("VOICE_ID") or kv.get("VOICE")
        tokens = []
        for b in bare:
            tokens += b.replace(",", " ").split()
        if not vid:
            vid = next((t for t in tokens if len(t) == 20 and t.isalnum()), None)
        if not key:
            key = next((t for t in tokens if t != vid), None)
    if not key:
        sys.exit("No API key. Set ELEVENLABS_API_KEY or Credentials/elevenlabs.txt")
    return key, (vid or DEFAULT_VOICE)

def main():
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    key, voice_id = load_creds()
    print("Using voice_id:", voice_id)
    client = ElevenLabs(api_key=key)
    audio = client.text_to_speech.convert(
        voice_id=voice_id, model_id=MODEL, text=NARRATION, output_format="mp3_44100_128",
        voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75, style=0.3,
                                     use_speaker_boost=True))
    with open(OUT, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)
    print("Wrote", OUT)
    os.makedirs(PUBLIC, exist_ok=True)
    shutil.copy(OUT, os.path.join(PUBLIC, "narration_konawe.mp3"))
    print("Copied to", os.path.join(PUBLIC, "narration_konawe.mp3"))

if __name__ == "__main__":
    main()

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
PUBLIC = os.path.join(HERE, "remotion-konawe", "public")
CRED = os.path.join(HERE, "..", "Credentials", "elevenlabs.txt")
DEFAULT_VOICE = "pNInz6obpgDQGcFmaJgB"
MODEL = "eleven_multilingual_v2"

NARRATION = (
    "Sepuluh tahun lalu, ini hutan. "
    "Sekarang? Lihat sendiri. "
    "Hijau berubah jadi merah — hutan dikupas menjadi tambang nikel. "
    "Bagaimana saya tahu? Dari satelit. Tiap tahun ia mengukur kehijauan — indeks NDVI. "
    "Hutan rapat nilainya tinggi; tanah terbuka, rendah. Ketika hutan dibuka, NDVI anjlok. "
    "Radar Sentinel-1, lewat metode SIRAD, bahkan mencatat kapan tiap petak dibuka. "
    "Hasilnya: ribuan hektar hutan lenyap. "
    "Tapi, marilah kita bersikap adil — kita timbang kedua sisinya. "
    "Di satu sisi, nikel memberikan keuntungan. Kawasan Industri Morosi di Konawe menargetkan hingga enam puluh ribu lapangan kerja. "
    "Hilirisasi melonjakkan nilai tambah nikel nasional, dari satu koma empat menjadi hampir tiga puluh lima miliar dolar — hanya dalam tiga tahun. "
    "Dan nikel adalah bahan baku baterai mobil listrik dunia. "
    "Tapi di sisi lain, ada ongkos yang jarang dihitung. "
    "Enam ribu hektar hutan lenyap, hanya di blok kecil ini. "
    "Padahal satu hektar hutan tropis bernilai sekitar dua ribu tujuh ratus dolar setiap tahun — air bersih, ikan, udara, penyerap karbon, dan keanekaragaman hayati. "
    "Artinya, kira-kira enam belas juta dolar jasa ekosistem hilang setiap tahun — berulang, selamanya. "
    "Tapi, bandingkan dengan adil. Angka tiga puluh lima miliar dolar dan enam puluh ribu pekerja itu skala nasional dan kawasan — dan itu pendapatan kotor. Ongkos tadi hanya dari satu blok kecil ini. "
    "Lagipula, enam belas juta dolar setahun pun baru lantai. Melenyapkan hutan ini melepas sekitar empat setengah juta ton karbon dioksida — setara puluhan hingga ratusan juta dolar, sekali lepas. "
    "Dan karena mengalir tiap tahun, selamanya, nilai jasa ekosistem yang hilang — bila dihitung sebagai aset — menembus tiga ratus juta dolar. "
    "Lalu, siapa yang untung dan siapa yang menanggung? Keuntungan mengalir ke perusahaan dan kas negara; ongkosnya ditanggung warga, nelayan, dan generasi mendatang yang tak pernah diajak setuju. "
    "Dan ini bukan pilihan antara tambang atau hutan. Tambang bisa dilakukan dengan benar — jejak lebih kecil, hutan bernilai tinggi dijaga, reklamasi sungguhan. Kerusakan ini bisa dihindari. "
    "Yang ditambang, habis sekali keruk. Yang punah dari alam, hilang setiap tahun. "
    "Maka pertanyaannya untuk kita: haruskah kita kejar pendapatan, "
    "sambil menutup mata pada kerusakan dan ongkos lingkungannya?"
)

# Anchor phrases -> cue names. The video reads konawe_cues.json (seconds) to sync scenes.
ANCHORS = {
    "cap_merah": "Hijau berubah jadi merah",
    "ndvi": "Bagaimana saya tahu",
    "sirad": "Radar Sentinel-1",
    "map": "Hasilnya: ribuan hektar",
    "balance": "Tapi, marilah kita bersikap adil",
    "question": "Maka pertanyaannya",
}

def compute_cues(characters, starts):
    text = "".join(characters)
    cues = {}
    for name, phrase in ANCHORS.items():
        i = text.find(phrase)
        if 0 <= i < len(starts):
            cues[name] = round(float(starts[i]), 2)
    if starts:
        cues["total"] = round(float(starts[-1]), 2)
    return cues

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
    import base64
    import json
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    key, voice_id = load_creds()
    print("Using voice_id:", voice_id)
    client = ElevenLabs(api_key=key)
    vs = VoiceSettings(stability=0.5, similarity_boost=0.75, style=0.3, use_speaker_boost=True)

    def get(o, *keys):
        for k in keys:
            if hasattr(o, k):
                return getattr(o, k)
            try:
                return o[k]
            except Exception:
                pass
        return None

    cues = None
    try:                                    # try timestamped TTS for auto-sync
        res = client.text_to_speech.convert_with_timestamps(
            voice_id=voice_id, model_id=MODEL, text=NARRATION,
            output_format="mp3_44100_128", voice_settings=vs)
        with open(OUT, "wb") as f:
            f.write(base64.b64decode(get(res, "audio_base_64", "audio_base64")))
        align = get(res, "alignment")
        cues = compute_cues(get(align, "characters"),
                            get(align, "character_start_times_seconds"))
        print("Timestamps OK. Cues:", cues)
    except Exception as e:                   # fallback: plain audio, video uses fraction timing
        print("convert_with_timestamps unavailable -> plain audio:", e)
        audio = client.text_to_speech.convert(
            voice_id=voice_id, model_id=MODEL, text=NARRATION,
            output_format="mp3_44100_128", voice_settings=vs)
        with open(OUT, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)

    print("Wrote", OUT)
    os.makedirs(PUBLIC, exist_ok=True)
    shutil.copy(OUT, os.path.join(PUBLIC, "narration_konawe.mp3"))
    print("Copied mp3 to public/")
    if cues:
        cj = os.path.join(HERE, "konawe_cues.json")
        json.dump(cues, open(cj, "w"), indent=2)
        shutil.copy(cj, os.path.join(PUBLIC, "konawe_cues.json"))
        print("Wrote konawe_cues.json -> public/")

if __name__ == "__main__":
    main()

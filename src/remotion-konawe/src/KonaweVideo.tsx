import React from "react";
import {
  AbsoluteFill, Audio, OffthreadVideo, Img, Sequence,
  staticFile, interpolate, spring, Easing, useCurrentFrame, useVideoConfig,
} from "remotion";

// Assets in public/: konawe_timelapse.mp4, sirad_konawe.png, sirad_konawe_map.png, narration_konawe.mp3
// Balanced narrative: damage → economy → true cost (Neraca) → closing question.
// Beats are FRACTIONS of total duration, so they auto-fit any narration length.

const END_CARD = "Mana buktinya?\nAda di citra satelit.\n@jalmiburung 🛰️";

// scene boundaries (fractions)
// Fraction fallback (used only if konawe_cues.json is missing). The Neraca infographic
// window (balance→question) is the longest so the audience can read it.
const FALLBACK: Record<string, number> = {
  cap_merah: 0.06, ndvi: 0.14, sirad: 0.24, map: 0.34, balance: 0.45, question: 0.88,
};

type Cues = Record<string, number> | null;

const Caption: React.FC<{text: string; durFrames: number}> = ({text, durFrames}) => {
  const f = useCurrentFrame();
  const opacity = interpolate(f, [0, 8, durFrames - 8, durFrames], [0, 1, 1, 0],
    {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return (
    <AbsoluteFill style={{justifyContent: "flex-end", alignItems: "center", padding: "0 60px 90px"}}>
      <div style={{
        opacity, background: "rgba(0,0,0,0.5)", borderRadius: 18, padding: "18px 28px",
        color: "white", fontFamily: "Inter, Arial, sans-serif", fontWeight: 800, fontSize: 46,
        lineHeight: 1.25, textAlign: "center", textShadow: "0 2px 8px rgba(0,0,0,0.9)", maxWidth: "90%",
      }}>{text}</div>
    </AbsoluteFill>
  );
};

const TimelapseBg: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const scale = interpolate(f, [0, 20 * fps], [1.05, 1.18],
    {extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic)});
  return (
    <AbsoluteFill style={{transform: `scale(${scale})`, transformOrigin: "50% 45%"}}>
      <OffthreadVideo src={staticFile("konawe_timelapse.mp4")} muted
        style={{width: "100%", height: "100%", objectFit: "cover"}} />
    </AbsoluteFill>
  );
};

const NDVIScale: React.FC = () => {
  const f = useCurrentFrame();
  const drop = interpolate(f, [12, 70], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return (
    <AbsoluteFill style={{background: "rgb(8,14,10)", justifyContent: "center", alignItems: "center"}}>
      <div style={{
        position: "relative", width: 120, height: 520, borderRadius: 12, border: "2px solid #fff",
        background: "linear-gradient(to bottom, #006837, #66bd63, #fee08b, #d73027, #7a3b12)",
      }}>
        <div style={{
          position: "absolute", left: -22, top: `${drop * 100}%`, transform: "translateY(-50%)",
          width: 0, height: 0, borderTop: "13px solid transparent", borderBottom: "13px solid transparent",
          borderLeft: "22px solid white",
        }} />
      </div>
      <div style={{position: "absolute", left: "57%", top: "29%", color: "#9be29b",
        fontFamily: "Inter, Arial", fontWeight: 800, fontSize: 32}}>Hutan — NDVI tinggi</div>
      <div style={{position: "absolute", left: "57%", top: "63%", color: "#e0a16a",
        fontFamily: "Inter, Arial", fontWeight: 800, fontSize: 32}}>Tanah terbuka — rendah</div>
      <div style={{position: "absolute", bottom: 110, width: "100%", textAlign: "center",
        color: "#eafff0", fontWeight: 800, fontSize: 40, fontFamily: "Inter, Arial",
        textShadow: "0 2px 8px #000"}}>Hutan dibuka → NDVI anjlok</div>
    </AbsoluteFill>
  );
};

const SiradReveal: React.FC = () => {
  const f = useCurrentFrame();
  const op = interpolate(f, [0, 15], [0, 1], {extrapolateRight: "clamp"});
  return (
    <AbsoluteFill style={{background: "rgb(8,14,10)", justifyContent: "center", alignItems: "center"}}>
      <Img src={staticFile("sirad_konawe.png")}
        style={{width: "84%", height: "66%", objectFit: "contain", opacity: op}} />
      <div style={{position: "absolute", top: 56, display: "flex", gap: 24,
        fontFamily: "Inter, Arial", fontWeight: 700, fontSize: 26, textShadow: "0 2px 8px #000"}}>
        <span style={{color: "#ffffff"}}>⬜ hutan utuh</span>
        <span style={{color: "#ffff66"}}>🟨 dibuka 2020–26</span>
        <span style={{color: "#ff6b6b"}}>🟥 2018–20</span>
      </div>
      <div style={{position: "absolute", bottom: 90, width: "100%", textAlign: "center",
        color: "#eafff0", fontWeight: 800, fontSize: 36, fontFamily: "Inter, Arial",
        textShadow: "0 2px 8px #000"}}>SIRAD: radar mencatat kapan hutan dibuka</div>
    </AbsoluteFill>
  );
};

const MapResult: React.FC = () => {
  const f = useCurrentFrame();
  const op = interpolate(f, [0, 12], [0, 1], {extrapolateRight: "clamp"});
  return (
    <AbsoluteFill style={{backgroundColor: "white"}}>
      <Img src={staticFile("sirad_konawe_map.png")}
        style={{width: "100%", height: "100%", objectFit: "contain", opacity: op}} />
    </AbsoluteFill>
  );
};

// "Neraca pembangunan" infographic (sourced figures) — built by make_konawe_neraca.py
const BalanceScene: React.FC = () => {
  const f = useCurrentFrame();
  const op = interpolate(f, [0, 15], [0, 1], {extrapolateRight: "clamp"});
  return (
    <AbsoluteFill style={{backgroundColor: "white"}}>
      <Img src={staticFile("konawe_neraca.png")}
        style={{width: "100%", height: "100%", objectFit: "contain", opacity: op}} />
    </AbsoluteFill>
  );
};

const QuestionScene: React.FC = () => {
  const f = useCurrentFrame();
  const op = interpolate(f, [0, 18], [0, 1], {extrapolateRight: "clamp"});
  return (
    <AbsoluteFill style={{background: "black", justifyContent: "center", alignItems: "center", padding: 80}}>
      <div style={{opacity: op, color: "white", fontFamily: "Inter, Arial, sans-serif", fontWeight: 800,
        fontSize: 54, lineHeight: 1.4, textAlign: "center", textShadow: "0 2px 10px #000"}}>
        Haruskah kita kejar pendapatan,<br />sambil menutup mata pada kerusakan<br />dan ongkos lingkungannya?
      </div>
    </AbsoluteFill>
  );
};

export const KonaweVideo: React.FC<{cues?: Cues}> = ({cues}) => {
  const {fps, durationInFrames} = useVideoConfig();
  const D = durationInFrames;
  // cue → frame: real timestamp from konawe_cues.json if present, else fraction fallback
  const t = (name: string) => {
    const sec = cues && cues[name] != null ? cues[name] : null;
    return sec != null ? Math.round(sec * fps) : Math.round((FALLBACK[name] ?? 0) * D);
  };
  const seg = (a: number, b: number) => Math.max(1, b - a);

  const tCap = t("cap_merah"), tNDVI = t("ndvi"), tSIRAD = t("sirad"),
        tMAP = t("map"), tBAL = t("balance"), tQ = t("question");
  const endCardFrames = Math.min(2 * fps, Math.round(D * 0.05));
  const narrationEnd = D - endCardFrames;
  const frame = useCurrentFrame();
  const pop = spring({frame: frame - narrationEnd, fps, config: {damping: 14}});

  const caps = [
    {from: 0, to: tCap, text: "Sepuluh tahun lalu, ini hutan."},
    {from: tCap, to: tNDVI, text: "Hijau → merah: hutan jadi tambang nikel."},
    {from: tMAP, to: Math.min(tBAL, tMAP + 9 * fps), text: "Ribuan hektar hutan lenyap."},
  ];

  return (
    <AbsoluteFill style={{backgroundColor: "black"}}>
      <Sequence from={0} durationInFrames={seg(0, tNDVI)}><TimelapseBg /></Sequence>
      <Sequence from={tNDVI} durationInFrames={seg(tNDVI, tSIRAD)}><NDVIScale /></Sequence>
      <Sequence from={tSIRAD} durationInFrames={seg(tSIRAD, tMAP)}><SiradReveal /></Sequence>
      <Sequence from={tMAP} durationInFrames={seg(tMAP, tBAL)}><MapResult /></Sequence>
      <Sequence from={tBAL} durationInFrames={seg(tBAL, tQ)}><BalanceScene /></Sequence>
      <Sequence from={tQ} durationInFrames={seg(tQ, narrationEnd)}><QuestionScene /></Sequence>

      <Audio src={staticFile("narration_konawe.mp3")} />

      {caps.map((c, i) => (
        <Sequence key={i} from={c.from} durationInFrames={seg(c.from, c.to)}>
          <Caption text={c.text} durFrames={seg(c.from, c.to)} />
        </Sequence>
      ))}

      <Sequence from={narrationEnd} durationInFrames={endCardFrames}>
        <AbsoluteFill style={{justifyContent: "center", alignItems: "center", backgroundColor: "rgba(0,0,0,0.65)"}}>
          <div style={{
            transform: `scale(${0.8 + 0.2 * pop})`, opacity: pop,
            color: "white", fontFamily: "Inter, Arial, sans-serif", fontWeight: 800,
            fontSize: 64, lineHeight: 1.3, textAlign: "center", whiteSpace: "pre-line",
            textShadow: "0 2px 10px rgba(0,0,0,0.95)",
          }}>{END_CARD}</div>
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};

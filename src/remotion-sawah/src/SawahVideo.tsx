import React from "react";
import {
  AbsoluteFill, Audio, OffthreadVideo, Img, Sequence, Loop,
  staticFile, interpolate, spring, Easing, useCurrentFrame, useVideoConfig,
} from "remotion";
import {PixelGrid, SideBySide, PhenologyCurve, Pipeline} from "./MethodExplainer";

// Needs public/paddy_java.png (copy from the s1 repo). Set false to preview without it.
const SHOW_PADDY_MAP = true;

const END_CARD = "Mana buktinya?\nAda di citra satelit.\n@jalmiburung 🛰️";

// Bottom captions ONLY for beats without a full-screen explainer (Act 2 = explainer titles).
const CAPTIONS: {from: number; to: number; text: string}[] = [
  {from: 0,  to: 5,  text: "Sepuluh tahun lalu, ini sawah."},
  {from: 5,  to: 13, text: "Merah = bangunan (radar Sentinel-1). Merahnya meluas."},
  {from: 13, to: 19, text: "Bagaimana saya tahu? Dari radar."},
  {from: 60, to: 69, text: "Sawah Jawa 2024/25: ± 2,28 juta ha."},
  {from: 69, to: 76, text: "Tapi terus menyusut — beralih fungsi."},
  {from: 76, to: 84, text: "Dari mana kita makan di 2045?"},
  {from: 84, to: 92, text: "Penduduk naik, lahan turun. Indonesia Emas atau Indonesia Lapar?"},
];

const Caption: React.FC<{text: string; durFrames: number}> = ({text, durFrames}) => {
  const f = useCurrentFrame();
  const opacity = interpolate(f, [0, 8, durFrames - 8, durFrames], [0, 1, 1, 0],
    {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return (
    <AbsoluteFill style={{justifyContent: "flex-end", alignItems: "center", padding: "0 60px 90px"}}>
      <div style={{
        opacity, background: "rgba(0,0,0,0.45)", borderRadius: 18, padding: "18px 28px",
        color: "white", fontFamily: "Inter, Arial, sans-serif", fontWeight: 800, fontSize: 46,
        lineHeight: 1.25, textAlign: "center", textShadow: "0 2px 8px rgba(0,0,0,0.9)", maxWidth: "90%",
      }}>{text}</div>
    </AbsoluteFill>
  );
};

// Act 1-2 background: time-lapse with a gentle push-in
const TimelapseBg: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const scale = interpolate(f, [0, 19 * fps], [1.05, 1.18],
    {extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic)});
  return (
    <AbsoluteFill style={{transform: `scale(${scale})`, transformOrigin: "50% 45%"}}>
      <OffthreadVideo src={staticFile("urban_sprawl.mp4")} muted
        style={{width: "100%", height: "100%", objectFit: "cover"}} />
    </AbsoluteFill>
  );
};

// Act 3-4 background: Java paddy map (slow zoom) + scrim for legibility
const PaddyBg: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const scale = interpolate(f, [0, 36 * fps], [1.0, 1.08], {extrapolateRight: "clamp"});
  // paddy seq starts at 60s; the 2045 question lands ~76s = local 16s -> dim the map then.
  const darken = interpolate(f, [16 * fps, 19 * fps], [0, 0.5],
    {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return (
    <AbsoluteFill style={{backgroundColor: "#0b1f12"}}>
      <AbsoluteFill style={{transform: `scale(${scale})`}}>
        {SHOW_PADDY_MAP ? (
          <Img src={staticFile("paddy_java.png")}
            style={{width: "100%", height: "100%", objectFit: "contain"}} />
        ) : (
          <AbsoluteFill style={{
            background: "radial-gradient(circle at 50% 45%, #1f6b3a 0%, #0b1f12 75%)",
          }} />
        )}
      </AbsoluteFill>
      {/* bottom scrim so captions read over the map */}
      <AbsoluteFill style={{
        background: "linear-gradient(to bottom, transparent 55%, rgba(0,0,0,0.65) 100%)",
        pointerEvents: "none",
      }} />
      {/* provocation dim as the 2045 question lands */}
      <AbsoluteFill style={{backgroundColor: "black", opacity: darken, pointerEvents: "none"}} />
    </AbsoluteFill>
  );
};

export const SawahVideo: React.FC = () => {
  const {fps, durationInFrames} = useVideoConfig();
  const S = (s: number) => Math.round(s * fps);
  const endCardFrames = 2 * fps;
  const narrationEnd = durationInFrames - endCardFrames;
  const frame = useCurrentFrame();
  const pop = spring({frame: frame - narrationEnd, fps, config: {damping: 14}});

  return (
    <AbsoluteFill style={{backgroundColor: "black"}}>
      {/* ACT 1-2 — time-lapse */}
      <Sequence from={0} durationInFrames={S(19)}>
        <TimelapseBg />
      </Sequence>
      {/* ACT 3-4 — Java paddy map */}
      <Sequence from={S(60)} durationInFrames={durationInFrames - S(60)}>
        <PaddyBg />
      </Sequence>
      {/* ACT 2 — animated method explainer (full-screen panels) */}
      <Sequence from={S(19)} durationInFrames={S(13)}><PixelGrid /></Sequence>
      <Sequence from={S(32)} durationInFrames={S(9)}><SideBySide /></Sequence>
      <Sequence from={S(41)} durationInFrames={S(10)}><PhenologyCurve /></Sequence>
      <Sequence from={S(51)} durationInFrames={S(9)}><Pipeline /></Sequence>
      {/* Narration */}
      <Audio src={staticFile("narration.mp3")} />
      {/* Captions (Act 1, pipeline, Act 3-4) */}
      {CAPTIONS.map((c, i) => (
        <Sequence key={i} from={S(c.from)} durationInFrames={S(c.to) - S(c.from)}>
          <Caption text={c.text} durFrames={S(c.to) - S(c.from)} />
        </Sequence>
      ))}
      {/* End card */}
      <Sequence from={narrationEnd} durationInFrames={endCardFrames}>
        <AbsoluteFill style={{justifyContent: "center", alignItems: "center", backgroundColor: "rgba(0,0,0,0.6)"}}>
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

import React from "react";
import {AbsoluteFill, Img, staticFile, interpolate, spring, useCurrentFrame, useVideoConfig} from "remotion";

const PANEL = "rgb(8,14,10)";          // opaque — no time-lapse bleed-through
const SHOW_STILLS = true;              // needs public/ndbi.png + public/ndvi.png
const titleStyle: React.CSSProperties = {
  position: "absolute", bottom: 110, width: "100%", textAlign: "center",
  color: "#eafff0", fontFamily: "Inter, Arial, sans-serif", fontWeight: 800, fontSize: 40,
  textShadow: "0 2px 8px rgba(0,0,0,0.9)",
};

// ---- Scene A: a satellite tile zoomed to pixels = numbers ------------
export const PixelGrid: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const appear = spring({frame: f, fps, config: {damping: 14}});
  const N = 6, cell = 110, gap = 8;
  const size = N * cell + (N - 1) * gap;
  const cells: React.ReactNode[] = [];
  for (let i = 0; i < N * N; i++) {
    const r = Math.floor(i / N), c = i % N;
    const show = interpolate(f, [i * 1.2 + 8, i * 1.2 + 20], [0, 1],
      {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
    const g = 80 + ((i * 37) % 130);
    cells.push(
      <div key={i} style={{
        position: "absolute", left: c * (cell + gap), top: r * (cell + gap),
        width: cell, height: cell, background: `rgb(38,${g},58)`,
        display: "flex", alignItems: "center", justifyContent: "center",
        color: "white", fontFamily: "monospace", fontWeight: 700, fontSize: 28,
      }}>
        <span style={{opacity: show}}>{60 + ((i * 53) % 160)}</span>
      </div>
    );
  }
  return (
    <AbsoluteFill style={{background: PANEL, justifyContent: "center", alignItems: "center"}}>
      <div style={{transform: `scale(${0.7 + 0.3 * appear})`, width: size, height: size, position: "relative"}}>
        {cells}
      </div>
      <div style={titleStyle}>Radar Sentinel-1 = angka, bukan foto</div>
    </AbsoluteFill>
  );
};

// ---- Scene B: spectral signatures (veg / water / urban) -------------
export const SpectralCurve: React.FC = () => {
  const f = useCurrentFrame();
  const draw = interpolate(f, [8, 80], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  const off = 1 - draw;
  const line = (d: string, color: string) => (
    <path d={d} fill="none" stroke={color} strokeWidth={2.5}
      vectorEffect="non-scaling-stroke" pathLength={1}
      strokeDasharray={1} strokeDashoffset={off} strokeLinecap="round" />
  );
  return (
    <AbsoluteFill style={{background: PANEL, justifyContent: "center", alignItems: "center"}}>
      <svg width={840} height={520} viewBox="0 0 100 100" preserveAspectRatio="none">
        {/* y is inverted: smaller y = higher reflectance */}
        {line("M3,82 L22,74 L38,76 L52,26 L74,24 L97,38", "#5fd36b") /* vegetation: NIR peak */}
        {line("M3,70 L22,73 L38,80 L52,86 L74,92 L97,96", "#4aa3ff") /* water: drops */}
        {line("M3,58 L22,57 L38,56 L52,55 L74,54 L97,53", "#d0d0d0") /* urban: flat-high */}
      </svg>
      <div style={{position: "absolute", top: 150, display: "flex", gap: 28, fontFamily: "Inter, Arial", fontWeight: 700, fontSize: 28}}>
        <span style={{color: "#5fd36b"}}>● Vegetasi</span>
        <span style={{color: "#4aa3ff"}}>● Air</span>
        <span style={{color: "#d0d0d0"}}>● Terbangun</span>
      </div>
      <div style={titleStyle}>Tiap objek, pantulan khas</div>
    </AbsoluteFill>
  );
};

// ---- Scene B2: side-by-side indices — NDBI (built-up) | NDVI (veg) --
export const SideBySide: React.FC = () => {
  const f = useCurrentFrame();
  const op = interpolate(f, [0, 12], [0, 1], {extrapolateRight: "clamp"});
  const half = (src: string, label: string, ph: string) => (
    <div style={{flex: 1, position: "relative", overflow: "hidden"}}>
      {SHOW_STILLS
        ? <Img src={staticFile(src)} style={{width: "100%", height: "100%", objectFit: "cover"}} />
        : <AbsoluteFill style={{background: ph}} />}
      <div style={{
        position: "absolute", top: 26, width: "100%", textAlign: "center", color: "#fff",
        fontFamily: "Inter, Arial", fontWeight: 800, fontSize: 34, textShadow: "0 2px 8px #000",
      }}>{label}</div>
    </div>
  );
  return (
    <AbsoluteFill style={{background: PANEL, opacity: op, flexDirection: "row"}}>
      {half("s1_builtup.png", "Bangunan — radar kuat & tetap", "#7a1f1f")}
      <div style={{width: 6, background: "#000"}} />
      {half("s1_sawah.png", "Sawah — radar berubah-ubah", "#1f6b3a")}
      <div style={titleStyle}>Bangunan tetap terang; sawah ikut musim</div>
    </AbsoluteFill>
  );
};

// ---- Scene C: paddy phenology — flood -> grow -> harvest ------------
export const PhenologyCurve: React.FC = () => {
  const f = useCurrentFrame();
  const draw = interpolate(f, [8, 35], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  const stages = [
    {x: 18, label: "Genangan", at: 30},
    {x: 50, label: "Tumbuh", at: 60},
    {x: 82, label: "Panen", at: 90},
  ];
  return (
    <AbsoluteFill style={{background: PANEL, justifyContent: "center", alignItems: "center"}}>
      <svg width={860} height={460} viewBox="0 0 100 100" preserveAspectRatio="none">
        {/* low (flood) -> rise (grow) -> peak -> drop (harvest) */}
        <path d="M3,86 L18,88 L34,58 L50,28 L66,26 L82,58 L97,82" fill="none"
          stroke="#7ee787" strokeWidth={4} vectorEffect="non-scaling-stroke"
          strokeLinecap="round" strokeLinejoin="round" opacity={draw} />
      </svg>
      {stages.map((s, i) => {
        const op = interpolate(f, [s.at, s.at + 12], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
        return (
          <div key={i} style={{
            position: "absolute", left: `${8 + s.x * 0.84}%`, top: 320, opacity: op,
            color: "#eafff0", fontFamily: "Inter, Arial", fontWeight: 700, fontSize: 26,
            transform: "translateX(-50%)",
          }}>{s.label}</div>
        );
      })}
      <div style={titleStyle}>Sawah punya tanda unik — radar menangkapnya</div>
    </AbsoluteFill>
  );
};

// ---- Scene D: pipeline — puluhan citra -> model -> peta -------------
export const Pipeline: React.FC = () => {
  const f = useCurrentFrame();
  const steps = ["Puluhan citra satelit", "↓", "Model klasifikasi", "↓", "Peta sawah seluruh Jawa"];
  return (
    <AbsoluteFill style={{
      background: PANEL, justifyContent: "center", alignItems: "center",
      flexDirection: "column", gap: 16,
    }}>
      {steps.map((s, i) => {
        const op = interpolate(f, [i * 10 + 6, i * 10 + 22], [0, 1],
          {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
        const big = i % 2 === 0;
        return (
          <div key={i} style={{
            opacity: op, color: big ? "#eafff0" : "#7ee787",
            fontFamily: "Inter, Arial", fontWeight: 800, fontSize: big ? 50 : 34,
            textShadow: "0 2px 8px #000",
          }}>{s}</div>
        );
      })}
    </AbsoluteFill>
  );
};

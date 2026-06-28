import React from "react";
import {Composition, staticFile} from "remotion";
import {getAudioDurationInSeconds} from "@remotion/media-utils";
import {KonaweVideo} from "./KonaweVideo";

const FPS = 30;

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="KonaweVideo"
      component={KonaweVideo}
      durationInFrames={FPS * 90}          // overwritten by calculateMetadata
      fps={FPS}
      width={1080}
      height={1080}
      defaultProps={{cues: null}}
      calculateMetadata={async () => {
        let durationInFrames = FPS * 90;
        try {
          const a = await getAudioDurationInSeconds(staticFile("narration_konawe.mp3"));
          durationInFrames = Math.ceil((a + 2) * FPS);
        } catch (e) { /* mp3 not in public/ yet */ }
        let cues: Record<string, number> | null = null;
        try {
          cues = await (await fetch(staticFile("konawe_cues.json"))).json();
        } catch (e) { /* no cues -> component falls back to fractions */ }
        return {durationInFrames, props: {cues}};
      }}
    />
  );
};

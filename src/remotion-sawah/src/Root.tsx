import React from "react";
import {Composition, staticFile} from "remotion";
import {getAudioDurationInSeconds} from "@remotion/media-utils";
import {SawahVideo} from "./SawahVideo";

const FPS = 30;

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="SawahVideo"
      component={SawahVideo}
      durationInFrames={FPS * 44}          // overwritten by calculateMetadata
      fps={FPS}
      width={1080}
      height={1080}                         // square; set 1350 for vertical 4:5
      calculateMetadata={async () => {
        // duration = narration length + 2s end card (falls back if mp3 not in public/ yet)
        try {
          const audio = await getAudioDurationInSeconds(staticFile("narration.mp3"));
          return {durationInFrames: Math.ceil((audio + 2) * FPS)};
        } catch {
          return {durationInFrames: FPS * 44};
        }
      }}
    />
  );
};

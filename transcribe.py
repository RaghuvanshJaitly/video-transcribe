#!/usr/bin/env python3
"""
Transcribe an MP4 (or any audio/video file) locally with faster-whisper.
No upload limits, no time limits, runs fully offline after the model downloads.

Install:
    pip install faster-whisper

Usage:
    python transcribe_video.py video.mp4
    python transcribe_video.py video.mp4 --model large-v3 --language en
    python transcribe_video.py video.mp4 --device cuda --compute-type float16

Outputs (next to the video unless --out-dir is given):
    video.txt   plain transcript
    video.srt   subtitles with timestamps
"""

import argparse
import sys
from pathlib import Path

from faster_whisper import WhisperModel


def fmt_srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> None:
    p = argparse.ArgumentParser(description="Transcribe an MP4 video with Whisper.")
    p.add_argument("video", type=Path, help="Path to the .mp4 file")
    p.add_argument("--model", default="small",
                   help="tiny, base, small, medium, large-v3 (default: small)")
    p.add_argument("--language", default=None,
                   help="Language code like 'en'. Omit to auto-detect.")
    p.add_argument("--device", default="auto", help="auto, cpu, or cuda")
    p.add_argument("--compute-type", default="auto",
                   help="auto, int8 (fast on CPU), float16 (GPU), float32")
    p.add_argument("--out-dir", type=Path, default=None,
                   help="Where to write outputs (default: same folder as video)")
    args = p.parse_args()

    if not args.video.exists():
        sys.exit(f"File not found: {args.video}")

    out_dir = args.out_dir or args.video.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    txt_path = out_dir / f"{args.video.stem}.txt"
    srt_path = out_dir / f"{args.video.stem}.srt"

    print(f"Loading model '{args.model}'...")
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)

    print(f"Transcribing {args.video} ...")
    # faster-whisper decodes the audio track from the mp4 itself (via PyAV),
    # and streams segments, so long videos are fine.
    segments, info = model.transcribe(
        str(args.video),
        language=args.language,
        vad_filter=True,   # skips silence, speeds things up
        beam_size=5,
    )

    print(f"Detected language: {info.language} (p={info.language_probability:.2f})")
    total = info.duration or 0

    with open(txt_path, "w", encoding="utf-8") as txt, \
         open(srt_path, "w", encoding="utf-8") as srt:
        for i, seg in enumerate(segments, start=1):
            text = seg.text.strip()
            txt.write(text + "\n")
            srt.write(f"{i}\n{fmt_srt_time(seg.start)} --> {fmt_srt_time(seg.end)}\n{text}\n\n")
            txt.flush()
            srt.flush()

            if total:
                print(f"\r[{seg.end / total:6.1%}] {text[:70]:<70}", end="", flush=True)
            else:
                print(f"\r[{seg.end:8.1f}s] {text[:70]:<70}", end="", flush=True)

    print(f"\n\nDone.\n  Text: {txt_path}\n  SRT:  {srt_path}")


if __name__ == "__main__":
    main()
# Video Transcribe

A simple Python script that transcribes an MP4 video (or any audio/video file) to text, entirely on your own machine. It uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper), so there are no API keys, no accounts, no upload limits, and no time limits. Long videos work fine.

Made with Claude Code.

## Features

- Runs fully offline after the one-time model download
- Free: no API, no per-minute billing
- Outputs a plain text transcript (`.txt`) and timestamped subtitles (`.srt`)
- Writes results as it goes and shows progress, so hours-long videos are fine
- Auto-detects the spoken language, or you can set it manually
- Works on CPU (including Apple Silicon Macs) or an NVIDIA GPU

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Or install manually:

```bash
pip install faster-whisper "av==15.1.0"
```

> **Note:** `av` is pinned to an older version because the newest release (19.x) is incompatible with faster-whisper 1.2.1 and fails with `open() got an unexpected keyword argument 'metadata_errors'`.

## Usage

```bash
python3 transcribe.py video.mp4
```

This creates `video.txt` and `video.srt` next to the video.

### Options

| Option | Description | Default |
| --- | --- | --- |
| `--model` | `tiny`, `base`, `small`, `medium`, `large-v3` | `small` |
| `--language` | Language code such as `en`. Omit to auto-detect | auto |
| `--device` | `auto`, `cpu`, or `cuda` | `auto` |
| `--compute-type` | `auto`, `int8`, `float16`, `float32` | `auto` |
| `--out-dir` | Folder for the output files | same as the video |

### Examples

```bash
# Fast on a laptop CPU
python3 transcribe.py video.mp4 --model small --compute-type int8

# Best accuracy (slow on CPU)
python3 transcribe.py video.mp4 --model large-v3

# NVIDIA GPU
python3 transcribe.py video.mp4 --device cuda --compute-type float16

# English only, custom output folder
python3 transcribe.py video.mp4 --language en --out-dir transcripts/
```

## Notes

- The first run downloads the model (about 500 MB for `small`), so it may pause before transcribing starts.
- Larger models are more accurate but slower. If `small` misses words, try `medium`.
- No ffmpeg install is needed. Audio is decoded directly from the video file.

## Credits

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [OpenAI Whisper](https://github.com/openai/whisper) models

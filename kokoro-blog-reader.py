#!/usr/bin/env python3

import argparse
import logging
import os
import re
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

# Suppress only known upstream warnings; unexpected warnings remain visible.
warnings.filterwarnings(
    "ignore",
    message=r"dropout option adds dropout after all but last recurrent layer.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r"`torch\.nn\.utils\.weight_norm` is deprecated.*",
    category=FutureWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r"`torch\.jit\.script` is deprecated.*",
    category=FutureWarning,
)

# The HF Hub sends this as an X-HF-Warning response header, which
# huggingface_hub logs rather than raising through the warnings module.
logging.getLogger("huggingface_hub.utils._http").addFilter(
    lambda record: "unauthenticated requests to the HF Hub" not in record.getMessage()
)

os.environ.setdefault("HF_HUB_DISABLE_IMPLICIT_TOKEN", "1")

import numpy as np
import soundfile as sf
from kokoro import KPipeline


VOICES = {
    "bm_daniel": "b",
    "bm_fable": "b",
    "bf_emma": "b",
    "bf_isabella": "b",

    "am_michael": "a",
    "am_liam": "a",
    "af_heart": "a",
    "af_bella": "a",
}

DEFAULT_SPEED = 0.8


def markdown_to_speech_text(markdown: str) -> str:
    """Remove common Markdown syntax while preserving readable article text."""

    # Remove YAML front matter.
    markdown = re.sub(
        r"\A---\s*\n.*?\n---\s*(?:\n|$)",
        "",
        markdown,
        flags=re.DOTALL,
    )

    # Remove fenced code blocks entirely.
    markdown = re.sub(r"```.*?```", "", markdown, flags=re.DOTALL)
    markdown = re.sub(r"~~~.*?~~~", "", markdown, flags=re.DOTALL)

    # Remove HTML comments and tags.
    markdown = re.sub(r"<!--.*?-->", "", markdown, flags=re.DOTALL)
    markdown = re.sub(r"<[^>]+>", "", markdown)

    # Remove images, keeping no alt-text narration.
    markdown = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", markdown)

    # Convert links to their visible text.
    markdown = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", markdown)

    # Remove reference-style link definitions.
    markdown = re.sub(r"^\s*\[[^\]]+\]:\s+\S+.*$", "", markdown, flags=re.MULTILINE)

    # Remove headings, blockquotes and list markers.
    markdown = re.sub(r"^\s{0,3}#{1,6}\s*", "", markdown, flags=re.MULTILINE)
    markdown = re.sub(r"^\s*>\s?", "", markdown, flags=re.MULTILINE)
    markdown = re.sub(r"^\s*[-+*]\s+", "", markdown, flags=re.MULTILINE)
    markdown = re.sub(r"^\s*\d+[.)]\s+", "", markdown, flags=re.MULTILINE)

    # Remove horizontal rules.
    markdown = re.sub(r"^\s*([-*_])(?:\s*\1){2,}\s*$", "", markdown, flags=re.MULTILINE)

    # Remove common inline formatting characters.
    markdown = markdown.replace("**", "").replace("__", "")
    markdown = markdown.replace("~~", "").replace("`", "")
    markdown = re.sub(r"(?<!\w)[*_](?=\S)|(?<=\S)[*_](?!\w)", "", markdown)

    # Collapse whitespace while retaining paragraph breaks.
    paragraphs = [
        re.sub(r"[ \t]+", " ", p).strip()
        for p in re.split(r"\n\s*\n", markdown)
    ]

    return "\n\n".join(p for p in paragraphs if p)


def encode_mp3(wav_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel", "error",
            "-i", str(wav_path),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:a", "libmp3lame",
            "-q:a", "2",
            str(output_path),
        ],
        check=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an MP3 narration from a Markdown article using Kokoro."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input Markdown file.",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Output MP3 file.",
    )
    parser.add_argument(
        "--voice",
        required=True,
        choices=sorted(VOICES),
        help="Kokoro voice to use.",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=DEFAULT_SPEED,
        help=f"Speech speed (default: {DEFAULT_SPEED}).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.input.is_file():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        return 2

    if args.output.suffix.lower() != ".mp3":
        print("Error: output filename must end in .mp3", file=sys.stderr)
        return 2

    if args.speed <= 0:
        print("Error: --speed must be greater than 0", file=sys.stderr)
        return 2

    markdown = args.input.read_text(encoding="utf-8")
    text = markdown_to_speech_text(markdown)

    if not text:
        print("Error: no narratable text found in input file.", file=sys.stderr)
        return 2

    lang_code = VOICES[args.voice]

    print(f"Input:  {args.input}")
    print(f"Output: {args.output}")
    print(f"Voice:  {args.voice}")
    print(f"Speed:  {args.speed}")

    pipeline = KPipeline(
        lang_code=lang_code,
        repo_id="hexgrad/Kokoro-82M",
    )

    audio_parts = [
        audio
        for _, _, audio in pipeline(
            text,
            voice=args.voice,
            speed=args.speed,
        )
    ]

    if not audio_parts:
        print("Error: Kokoro returned no audio.", file=sys.stderr)
        return 1

    audio = np.concatenate(audio_parts)

    with tempfile.NamedTemporaryFile(suffix=".wav") as temp:
        wav_path = Path(temp.name)
        sf.write(wav_path, audio, 24000)
        encode_mp3(wav_path, args.output)

    print(f"Created: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Kokoro Blog Reader

## Native macOS

Requires an Apple Silicon Mac, Homebrew `ffmpeg` and a Python 3.10–3.12
interpreter (`brew install ffmpeg python@3.12`). On Linux or Intel Macs,
use Docker instead.

```bash
./kokoro-blog-reader \
  article.md article.mp3 \
  --voice bm_fable \
  --speed 1.10
```

The first run creates `.venv` in the repo root, upgrades pip and installs
`requirements.txt`. That repeats automatically whenever
`requirements.txt` changes; delete `.venv` to force a rebuild.

The Hugging Face cache is `./.cache/huggingface` if it exists, otherwise
`~/.cache/huggingface`. Set `HF_HOME` to override. Set `KOKORO_PYTHON` to
pick a specific interpreter.

To call it from anywhere, symlink it onto your `PATH`:

```bash
ln -s "$PWD/kokoro-blog-reader" /opt/homebrew/bin/kokoro-blog-reader
```

## Docker

Build:

```bash
docker build -t kokoro-blog-reader .
```

Run from the directory containing the article:

```bash
mkdir -p .cache/huggingface

docker run --rm \
  -v "$PWD:/work" \
  -v "$PWD/.cache/huggingface:/root/.cache/huggingface" \
  kokoro-blog-reader \
  article.md article.mp3 \
  --voice bm_daniel
```

Available voices:

- `bm_daniel`
- `bm_fable`
- `bf_emma`
- `bf_isabella`
- `am_michael`
- `am_liam`
- `af_heart`
- `af_bella`

Default speed is `0.80`. Override it with:

```bash
docker run --rm \
  -v "$PWD:/work" \
  -v "$PWD/.cache/huggingface:/root/.cache/huggingface" \
  kokoro-blog-reader \
  article.md article.mp3 \
  --voice bm_fable \
  --speed 1.10
```

Because `/work` is the host's current directory, the generated
MP3 appears directly in `$PWD`.

The Hugging Face model cache is persisted in:

```text
$PWD/.cache/huggingface
```

On a Linux host, add `--user "$(id -u):$(id -g)"` so the MP3 and cache
files are owned by you rather than root:

```bash
docker run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$PWD:/work" \
  -v "$PWD/.cache/huggingface:/root/.cache/huggingface" \
  kokoro-blog-reader \
  article.md article.mp3 \
  --voice bm_fable
```

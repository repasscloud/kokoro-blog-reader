# Kokoro Blog Reader

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

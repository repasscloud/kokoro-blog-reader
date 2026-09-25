# syntax=docker/dockerfile:1

FROM python:3.12-slim-trixie

LABEL org.opencontainers.image.title="kokoro-blog-reader" \
      org.opencontainers.image.description="Narrate Markdown articles to MP3 with Kokoro TTS" \
      org.opencontainers.image.source="https://github.com/repasscloud/kokoro-blog-reader"

ENV TZ=Australia/Sydney \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    HF_HOME=/root/.cache/huggingface

# Runtime OS packages only. espeak-ng isn't needed from APT: Kokoro's
# fallback phonemizer loads the copy bundled in the espeakng-loader wheel.
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ffmpeg \
        tzdata \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/* /var/log/apt/*

COPY requirements.txt /tmp/requirements.txt

# Install the pinned torch from the CPU-only index first so Kokoro cannot pull
# CUDA/NVIDIA/Triton; the second install then sees torch as already satisfied.
# Afterwards, drop PyTorch headers/tests and bytecode caches that inference
# doesn't need.
RUN python -m pip install --upgrade pip \
    && python -m pip install \
        --index-url https://download.pytorch.org/whl/cpu \
        "$(grep -E '^torch==' /tmp/requirements.txt)" \
    && python -m pip install -r /tmp/requirements.txt \
    && SITE_PACKAGES="$(python -c 'import sysconfig; print(sysconfig.get_path("purelib"))')" \
    && rm -rf \
        "$SITE_PACKAGES/torch/test" \
        "$SITE_PACKAGES/torch/include" \
        /tmp/requirements.txt \
        /root/.cache/pip \
    && find "$SITE_PACKAGES" -type d -name '__pycache__' -prune -exec rm -rf '{}' + \
    && find "$SITE_PACKAGES" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete

# Let the image run as a non-root host user (docker run --user) while keeping
# the documented /root/.cache/huggingface mount point.
RUN mkdir -p "$HF_HOME" \
    && chmod 755 /root /root/.cache \
    && chmod 1777 "$HF_HOME"

WORKDIR /work

COPY kokoro-blog-reader.py /usr/local/bin/kokoro-blog-reader

ENTRYPOINT ["python", "/usr/local/bin/kokoro-blog-reader"]

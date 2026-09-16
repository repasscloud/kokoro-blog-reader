FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Australia/Sydney \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Install only required runtime OS packages, then remove all APT metadata/cache.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        espeak-ng \
        ffmpeg \
        tzdata \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /var/cache/apt/* \
        /var/log/apt/*

# Install CPU-only PyTorch first so Kokoro cannot pull CUDA/NVIDIA/Triton.
#
# PIP_NO_CACHE_DIR=1 prevents pip from retaining downloaded wheels.
#
# Remove PyTorch development/test content and Python bytecode/cache files
# that aren't required for Kokoro inference.
RUN python -m pip install --upgrade pip \
    && python -m pip install \
        --index-url https://download.pytorch.org/whl/cpu \
        torch \
    && python -m pip install \
        kokoro \
        soundfile \
        numpy \
    && rm -rf \
        /usr/local/lib/python3.12/site-packages/torch/test \
        /usr/local/lib/python3.12/site-packages/torch/include \
        /root/.cache/pip \
    && find /usr/local/lib/python3.12/site-packages \
        -type d -name '__pycache__' \
        -prune -exec rm -rf '{}' + \
    && find /usr/local/lib/python3.12/site-packages \
        -type f \( -name '*.pyc' -o -name '*.pyo' \) \
        -delete

WORKDIR /work

COPY kokoro-blog-reader.py /usr/local/bin/kokoro-blog-reader

ENTRYPOINT ["python", "/usr/local/bin/kokoro-blog-reader"]
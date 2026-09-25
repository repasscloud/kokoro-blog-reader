# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-09-25

### Added

- `kokoro-blog-reader` launcher for running natively on Apple Silicon macOS.
  It creates `.venv`, installs `requirements.txt`, and uses
  `./.cache/huggingface` or `~/.cache/huggingface` as the model cache.
  It exits with an error on any other OS or architecture.
- `requirements.txt` with pinned top-level dependencies, shared by the
  Docker image and the native launcher.
- The Docker image supports `docker run --user` for non-root hosts.

### Changed

- The Docker image now installs from `requirements.txt` on a
  `python:3.12-slim-trixie` base. The spaCy `en_core_web_sm` model is
  baked in, so containers no longer download it on every run.
- Removed the APT `espeak-ng` package. Kokoro uses the copy bundled in the
  `espeakng-loader` wheel.

### Fixed

- The "unauthenticated requests to the HF Hub" message is now actually
  suppressed.

## [1.1.0] - 2026-09-20

### Added

- `README.md` with full setup, configuration reference, volume/model-caching
  notes, `docker-compose` example, and troubleshooting gotchas.
- `CHANGELOG.md` (this file).
- CI: native `linux/arm64` builds on `ubuntu-24.04-arm`, replacing QEMU
  emulation. The build job is now a matrix (`linux/amd64` on `ubuntu-latest`,
  `linux/arm64` on `ubuntu-24.04-arm`), with a separate `manifest` job that
  stitches the two single-arch images into one multi-arch manifest via
  `docker buildx imagetools create`.

### Changed

- Docker Hub image tags are now bare semver (`1.1.0`) instead of
  `v`-prefixed (`v1.2.0`), stripped from the git tag via
  `${GITHUB_REF_NAME#v}` in CI.
- Split the release workflow into three jobs (`validate`, `build`,
  `manifest`) instead of one, so tag validation runs once and each
  architecture builds independently.

## [1.0.0] - 2026-09-16

### Added

- Initial release

[Unreleased]: https://github.com/repasscloud/kokoro-blog-reader/compare/v1.2.0...main
[1.2.0]: https://github.com/repasscloud/kokoro-blog-reader/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/repasscloud/kokoro-blog-reader/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/repasscloud/kokoro-blog-reader/releases/tag/v1.0.0

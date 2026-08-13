# Patched OpenClaw gateway + microbiome conda runtimes.
# Build via scripts/build-openclaw-mgx-image.sh (applies patches on the pin
# commit, then this file). Do not FROM ghcr.io/openclaw/openclaw — those
# images do not include the exec-session-wake patch pack.
ARG OPENCLAW_IMAGE=openclaw:patched
FROM ${OPENCLAW_IMAGE}

USER root

ARG TARGETARCH=amd64
ARG MINIFORGE_VERSION=24.11.3-2
ARG MGX_ENVS=all
ENV CONDA_ROOT=/opt/conda \
    CONDA_EXE=/opt/conda/bin/conda \
    PATH=/opt/conda/bin:${PATH}

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      ca-certificates curl bzip2 \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    case "${TARGETARCH}" in \
      amd64) mf_arch=x86_64 ;; \
      arm64) mf_arch=aarch64 ;; \
      *) echo "unsupported TARGETARCH=${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    curl -fsSL -o /tmp/miniforge.sh \
      "https://github.com/conda-forge/miniforge/releases/download/${MINIFORGE_VERSION}/Miniforge3-${MINIFORGE_VERSION}-Linux-${mf_arch}.sh"; \
    bash /tmp/miniforge.sh -b -p /opt/conda; \
    rm -f /tmp/miniforge.sh; \
    /opt/conda/bin/conda config --system --set channel_priority strict; \
    /opt/conda/bin/conda clean -afy

COPY environments /opt/mgx/environments
COPY scripts/bootstrap-runtimes.sh /opt/mgx/scripts/bootstrap-runtimes.sh
COPY scripts/verify-runtimes.sh /opt/mgx/scripts/verify-runtimes.sh
RUN chmod +x /opt/mgx/scripts/*.sh

# Same recipes as a bare-metal host. Full stack is large (tens of GB).
RUN if [ "${MGX_ENVS}" = "all" ]; then \
      /opt/mgx/scripts/bootstrap-runtimes.sh --prefix /opt/conda --all; \
    else \
      /opt/mgx/scripts/bootstrap-runtimes.sh --prefix /opt/conda --only "${MGX_ENVS}"; \
    fi \
    && /opt/conda/bin/conda clean -afy \
    && chmod -R a+rX /opt/conda

COPY . /opt/openclaw-microbiome
RUN printf '%s\n' \
      'export CONDA_ROOT=/opt/conda' \
      'export CONDA_EXE=/opt/conda/bin/conda' \
      'export PATH="/opt/conda/bin:${PATH}"' \
      > /etc/profile.d/mgx-conda.sh \
    && chmod 644 /etc/profile.d/mgx-conda.sh

USER node
WORKDIR /app

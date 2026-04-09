# Dockerfile for QSBench v5.2.0
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV CUDA_VISIBLE_DEVICES=0

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-dev \
        python3-venv \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python3 -m pip install --upgrade pip setuptools wheel

COPY pyproject.toml .

COPY qsbench ./qsbench

COPY generate.py .

RUN pip3 install --no-cache-dir -e ".[dev]"

CMD ["python3", "-m", "qsbench.generate"]
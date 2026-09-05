FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libdbus-1-3 libegl1 libfontconfig1 libgl1 libglib2.0-0 libxkbcommon0 \
    libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-render-util0 xvfb \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -e '.[dev]'
COPY . .

FROM base AS test
CMD ["python", "-m", "pytest", "-q"]

FROM base AS gui-smoke
ENV QT_QPA_PLATFORM=offscreen ENGLISH_LEARNING_SKIP_WELCOME=1 ENGLISH_LEARNING_SMOKE_TEST=1
CMD ["python", "main.py"]

FROM base AS development
CMD ["python", "main.py"]

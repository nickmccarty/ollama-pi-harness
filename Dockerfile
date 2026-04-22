FROM python:3.11-slim

WORKDIR /app

# System deps: git (for git+ installs), build tools, ffmpeg (whisper)
RUN apt-get update && apt-get install -y --no-install-recommends \
        git build-essential curl ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps in layers for cache efficiency.
# PyTorch first (large, changes rarely) — CPU build here; GPU image uses base below.
RUN pip install --no-cache-dir torch==2.7.1 --extra-index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium --with-deps

COPY . .

EXPOSE 8765

CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8765"]

# -------------------------
# 1) Base Image
# -------------------------
FROM python:3.12-slim

# Disable Python .pyc files and buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -------------------------
# 2) Install system packages
# -------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -------------------------
# 3) Create app directory
# -------------------------
WORKDIR /app

# -------------------------
# 4) Copy Python dependencies
# -------------------------
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# -------------------------
# 5) Copy app source
# -------------------------
COPY . /app

# -------------------------
# 6) Expose port
# -------------------------
EXPOSE 3000

# -------------------------
# 7) Start Flask App
# Production = gunicorn
# -------------------------
CMD ["gunicorn", "-b", "0.0.0.0:3000", "app:app"]

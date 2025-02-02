FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
        build-essential \
        cmake \
        curl \
        g++ \
        gcc \
        git \
        libopenblas-openmp-dev \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN python -m pip install --upgrade pip && pip install --use-feature=fast-deps --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["python", "app.py"]
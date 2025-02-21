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

WORKDIR /onprem

COPY requirements.txt /onprem/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /onprem/

CMD ["python", "onprem_service.py"]
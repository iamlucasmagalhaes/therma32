FROM python:3.10

RUN apt-get update && apt-get install -y \
    git \
    wget \
    python3-venv \
    usbutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip install platformio

WORKDIR /project

CMD ["pio", "home", "--host", "0.0.0.0", "--port", "8000"]

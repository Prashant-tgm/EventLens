FROM python:3.10-slim

# Install system dependencies for OpenCV and AI models
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy requirements files
COPY requirements.txt requirements-ai.txt ./

# Install python packages
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-ai.txt

# Copy source code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

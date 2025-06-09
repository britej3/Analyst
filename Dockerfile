# Use an Ubuntu base image so the container matches
# a typical local Ubuntu environment
FROM ubuntu:22.04

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /app/data /app/logs /app/models

# Set environment variables
ENV PYTHONPATH=/app
ENV OLLAMA_HOST=0.0.0.0:11434

# Expose ports
EXPOSE 8000 11434

# Create startup script
COPY start.sh .
RUN chmod +x start.sh

# Start services
CMD ["./start.sh"]

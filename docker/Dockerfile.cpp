# Dockerfile for C++ execution
FROM gcc:latest

WORKDIR /app

# Install development tools
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

CMD ["bash"]

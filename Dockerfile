# Use a base image with Python
FROM python:3.10

LABEL authors="DeusN"

# Set the working directory
WORKDIR /

# Copy the local files to the container
COPY . .

# Ensure system packages and pip are installed
RUN apt-get update && \
    apt-get install --no-install-recommends -y git build-essential python3-dev bash curl && \
    rm -rf /var/lib/apt/lists/*

# Ensure pip is updated
RUN python -m pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port 8000 (change if needed)
EXPOSE 8000

# Run FastAPI (or Gradio)
CMD ["python", "launch.py"]
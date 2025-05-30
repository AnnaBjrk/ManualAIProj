FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libffi-dev \          
    build-essential \     
    && rm -rf /var/lib/apt/lists/*


# Copy requirements first (for better caching)
COPY app/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /

# Expose the port your app runs on
EXPOSE 8000

# Run the setup script to create tables and insert dummy data
CMD ["sh", "-c", "python app/setup.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
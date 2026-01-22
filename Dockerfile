FROM python:3.10-slim

# Install required system libraries
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev gcc build-essential pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/base.txt ./requirements/base.txt
COPY requirements/prod.txt ./requirements/prod.txt

# Install python dependencies
RUN pip install --no-cache-dir -r requirements/base.txt
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copy application code
COPY app ./app
COPY scripts ./scripts

# Set environment
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Command to run the application (overridden by docker-compose for dev)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

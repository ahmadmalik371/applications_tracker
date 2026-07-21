FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
COPY requirements-prod.txt ./
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application source
COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

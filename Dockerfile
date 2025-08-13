# Use Python 3.10 slim image as base
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into container
COPY . .

# Cloud Run sets $PORT, default to 8080 for local dev
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Run Streamlit app
CMD ["bash", "-lc", "streamlit run financialdata.py --server.port $PORT --server.address 0.0.0.0"]

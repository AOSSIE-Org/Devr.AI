FROM python:3.10-slim

WORKDIR /app

# Install dependencies first for better caching
COPY github_mcp_server/requirements.txt .
RUN pip install --upgrade pip && \
  pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
  pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory to /app
COPY . .

# Expose the port the app runs on
EXPOSE 8001

# Health check (optional but recommended best practice)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Start the server
CMD ["python", "start_github_mcp_server.py"]

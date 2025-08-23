FROM python:3.11-slim

WORKDIR /app

# Copy requirements file if it exists, otherwise we'll install common packages
COPY requirements.txt* ./

# Install Python dependencies
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; else pip install --no-cache-dir requests beautifulsoup4 selenium; fi

# Copy the application code
COPY . .

# Expose port (adjust if needed)
EXPOSE 4000

# Run the webbot script
CMD ["python", "webbot.py"]

# Use Python 3.14 slim image as base
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==2.0.1

# Copy dependency files
COPY pyproject.toml ./

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-root --no-interaction --no-ansi

# Copy application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8080
ENV RELOAD=false
ENV ANIMATION_MAX_SPEED=4

# Run the application
CMD ["python", "main.py"]

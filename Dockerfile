# Use an official, lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy just the requirements first to leverage Docker's caching
COPY requirements.txt .

# Install dependencies directly into the container
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port Gunicorn will use
EXPOSE 5001

# Command to run the application
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5001", "app:app"]
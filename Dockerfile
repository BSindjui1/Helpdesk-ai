# Start from an official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first — Docker caches this layer
# so it won't reinstall packages unless requirements.txt changes
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Tell Docker your app listens on port 5000
EXPOSE 5000

# Command to run when container starts
CMD ["python3", "app.py"]

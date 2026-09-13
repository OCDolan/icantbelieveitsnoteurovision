FROM python:3.12

# Set working directory
WORKDIR /app

# Copy requirements first for caching pip installs
COPY requirements.txt .

# Install dependencies
#RUN apt-get install python3-pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port your app runs on
EXPOSE 8000

# Define the entrypoint command
CMD ["./start.sh"]

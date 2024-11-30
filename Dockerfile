# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

ENV PORT 8080

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE $PORT

# Define environment variable
ENV NAME QuizardAPI

# Run app.py when the container launches
#CMD ["python", "app.py"]
CMD exec gunicorn --bind :$PORT --workers 1 --threads 1 --timeout 0 app:app


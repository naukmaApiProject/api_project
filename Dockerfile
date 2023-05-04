FROM python:3.9-slim-buster

ENV WEATHER_API_KEY=PXAMV42AU6LKXV828GP3UCWGH
ENV FLASK_RUN_HOST=0.0.0.0

# Install any necessary dependencies
RUN apt-get update && \
    apt-get install -y cron

# Set up a working directory for the application
WORKDIR /app

# Copy the Python scripts and cronjob file to the container
COPY . .

RUN pip install -r requirements.txt

# Set up the cronjob
RUN chmod 0644 cronjobs/cronjob_build_predictions && \
    crontab cronjobs/cronjob_build_predictions && \
    touch /var/log/cron.log

# Run the Flask server
CMD [ "flask", "--app", "api/predictions_endpoint.py", "run"]
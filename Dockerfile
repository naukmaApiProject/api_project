FROM python:3.9-slim-buster

# Install any necessary dependencies
RUN apt-get update && \
    apt-get install -y cron

# Set up a working directory for the application
WORKDIR /app

# Copy the Python scripts and cronjob file to the container
COPY . .

RUN pip install -r requirements.txt
# Set up the cronjob
RUN chmod 0644 cronjobs/cronjob_parse_data && \
    crontab cronjob_parse_data && \
    touch /var/log/cron.log

# Run the Flask server
CMD [ "python", "api/predictions_endpoint.py" ]
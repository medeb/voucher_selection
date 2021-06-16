# We build from python3.6 which provides a python3.6 insatlled ubuntu OS.
FROM python:3.7

# Set working directory within docker container

WORKDIR /app

# Copy python reqs
COPY requirements.txt ./

# Install reqs
RUN pip install --no-cache-dir -r requirements.txt

# Necessary Folders
# COPY controller ./controller
# COPY resources ./resources
# COPY service ./service

# ENV FLASK_APP=app.py


COPY . ./app
# RUN flask run

CMD [ "python", "/app/app/app.py" ]


# # Necessary Files
# COPY .env config.py stories.py boot.sh gunicorn.ini ./
# RUN chmod +x ./boot.sh
#
# # Expose port
# EXPOSE 8000
#
# # Specify entry point script
# ENTRYPOINT ["./boot.sh"]
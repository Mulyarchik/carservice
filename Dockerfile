FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies required by psycopg2
RUN apt-get update \
    && apt-get install -y postgresql postgresql-contrib gcc python3-dev musl-dev

# Set `/app` as working directory and copy all project files here
WORKDIR /app
COPY . .

# install pip dependencies
RUN pip install --upgrade pip
RUN pip install virtualenv && virtualenv -p python /app/venv
RUN pip install --user -r requirements.txt

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD "python" "manage.py" "runserver" "0.0.0.0:8080"

EXPOSE 8080
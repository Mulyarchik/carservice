FROM python:3.10-slim
# set work directory

WORKDIR /app
# set environment variables

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update \
    && apt-get install -y postgresql postgresql-contrib gcc python3-dev musl-dev

# install dependencies

RUN pip install --upgrade pip
COPY ./requirements.txt .

RUN pip install virtualenv && virtualenv -p python /app/venv
RUN python -m pip install -r requirements.txt
#copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

# run entrypoint.sh
RUN chmod +x /app/entrypoint.sh
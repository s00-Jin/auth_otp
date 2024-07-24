FROM python:3.9

ENV PYTHONBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on


RUN apt update && apt upgrade -y && apt install -y build-essential libssl-dev
RUN pip install "setuptools<58.0.0" "cmake==3.18.0"

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
COPY . /app/

CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--reload"]
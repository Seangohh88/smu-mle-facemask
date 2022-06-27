FROM gcr.io/deeplearning-platform-release/base-cpu
WORKDIR /app

COPY . /app

ENTRYPOINT ["python", "generatedata.py"]

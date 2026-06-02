FROM python:3.11-slim
WORKDIR /src
COPY ./requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt
COPY ./app /src/app
CMD ["fastapi", "run", "app/main.py", "--port", "80"]
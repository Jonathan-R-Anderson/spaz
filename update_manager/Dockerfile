FROM python:3.11-slim

WORKDIR /manager

COPY . .

RUN pip install --no-cache-dir jsonschema

CMD ["python", "app.py"]

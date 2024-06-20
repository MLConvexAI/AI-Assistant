FROM python:3-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="/app"

WORKDIR /app

COPY . /app

RUN python3 -m pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]

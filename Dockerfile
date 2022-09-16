# app/Dockerfile

FROM python:3.9-slim

EXPOSE 8501

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# hopefully cache the requirements
ADD ./requirements.txt ./requirements.txt 
# RUN pip3 install -r requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "-m", "main", "run", "streamlit_app.py","--server.port=8501", "--server.address=0.0.0.0"]
FROM ubuntu:18.04
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y python3-pip libpq-dev
RUN pip3 install --upgrade pip
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt
EXPOSE 5432:5432
CMD ["python3", "read_sheets.py"]

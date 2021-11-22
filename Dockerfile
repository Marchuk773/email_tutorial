FROM python:latest

RUN mkdir -p /code/

COPY requirements.txt /code/
WORKDIR /code/
RUN pip install -r requirements.txt
COPY . /code/
EXPOSE 5000
CMD ["python", "app.py"]
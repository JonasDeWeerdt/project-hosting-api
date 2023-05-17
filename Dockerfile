FROM python:3.10.0-slim
RUN apt-get update
RUN apt-get install git -y
RUN git clone https://github.com/JonasDeWeerdt/project-hosting-api.git
WORKDIR /code
EXPOSE 8000
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install python-jose[cryptography]
COPY ./project /code
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

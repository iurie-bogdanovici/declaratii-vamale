from python:3.10-slim

WORKDIR /app

COPY . /app

RUN apt-get update
RUN apt-get install libgl1-mesa-glx -y
RUN apt-get install 'ffmpeg'\
    'libsm6'\
    'libxext6'  -y

RUN apt-get install poppler-utils -y

RUN apt-get install tesseract-ocr -y
RUN apt-get install tesseract-ocr-jpn

RUN pip3 --no-cache install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["routes.py"]

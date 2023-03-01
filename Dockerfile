FROM python:3.8
COPY ./app /app
WORKDIR /app
RUN apt update -y
RUN apt install -y flac
RUN apt install -y portaudio19-dev
RUN apt install -y ffmpeg libsm6 libxext6
#RUN apt install -y alsa-base alsa-utils
RUN pip3 install --upgrade pip
RUN pip3 install cmake
RUN pip3 install -r requirements.txt
EXPOSE 80
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

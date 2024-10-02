FROM python:3.10
RUN apt-get update && apt-get install --no-install-recommends -y locales locales-all python3-pip tzdata
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata
RUN mkdir /billing_app
WORKDIR /billing_app
COPY ./requirements.txt .
RUN python3.10 -m pip install -r requirements.txt && rm -f requirements.txt
COPY ./config/config_loader.py ./config/config_loader.py
COPY ./src .
RUN chmod -R 777 ./
ENTRYPOINT ["python3.10", "billing_service.py"]
#ENTRYPOINT ["tail"]
#CMD ["-f","/dev/null"]
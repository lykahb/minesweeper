FROM python:3

RUN apt-get update && apt-get install -y libsqlite3-dev
RUN pip install pyramid SQLAlchemy

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app

RUN python setup.py develop
RUN initialize_minesweeper_db development.ini

EXPOSE 6543

CMD ["/usr/local/bin/pserve", "development.ini", "--reload"]
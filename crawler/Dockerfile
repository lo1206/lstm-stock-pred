FROM jupyter/tensorflow-notebook

WORKDIR /app

COPY ./crawler/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY ./crawler /app
COPY ./utils /app/utils

CMD python -u crawler.py
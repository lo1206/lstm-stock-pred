FROM jupyter/tensorflow-notebook

WORKDIR /app


COPY ./analysis/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY ./analysis /app
COPY ./utils /app/utils

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app"]
#CMD python app.py
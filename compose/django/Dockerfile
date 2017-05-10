FROM python:3.5.3

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements
RUN mkdir -p /static_root

RUN pip install -r /requirements/production.txt \
    && groupadd -r django \
    && useradd -r -g django django

COPY . /app
RUN chown -R django /app
RUN chown -R django /requirements
RUN chmod +x /requirements
RUN chown -R django /static_root
RUN chmod +x /static_root

COPY ./compose/django/celeryd /etc/default/celeryd
COPY ./compose/django/gunicorn.sh /gunicorn.sh
COPY ./compose/django/entrypoint.sh /entrypoint.sh
COPY ./compose/django/celery.sh /celery.sh
RUN sed -i 's/\r//' /entrypoint.sh \
    && sed -i 's/\r//' /gunicorn.sh \
    && sed -i 's/\r//' /celery.sh \
    && chmod +x /entrypoint.sh \
    && chown django /entrypoint.sh \
    && chmod +x /gunicorn.sh \
    && chown django /gunicorn.sh \
    && chmod +x /celery.sh \
    && chown django /celery.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]

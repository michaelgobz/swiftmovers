### Build and install packages
FROM python:3.11.0 as build-python

RUN apt-get -y update \
  && apt-get install -y gettext \
  # Cleanup apt cache
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

### Final image
FROM python:3.10.0-slim

RUN groupadd -r api && useradd -r -g api api

RUN apt-get update \
  && apt-get install -y \
  libcairo2 \
  libgdk-pixbuf2.0-0 \
  liblcms2-2 \
  libopenjp2-7 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libssl1.1 \
  libtiff5 \
  libwebp6 \
  libxml2 \
  libpq5 \
  shared-mime-info \
  mime-support \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/media /app/static \
  && chown -R api:api /app/

COPY --from=build-python /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=build-python /usr/local/bin/ /usr/local/bin/
COPY .. /app
WORKDIR /app

RUN python3 manage.py migrate
RUN python3 manage.py runserver

EXPOSE 8000
ENV PYTHONUNBUFFERED 1

CMD ["gunicorn", "--bind", ":8000", "--workers", "4", "--worker-class", "swiftmovers.asgi.gunicorn_worker.UvicornWorker", "swiftmovers.asgi:application"]
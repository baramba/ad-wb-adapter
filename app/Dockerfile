FROM python:3.11-slim as base

ARG WORKDIR=/code
ARG SRC_CODE_DIR=src
ARG USER=app
ARG GROUP=apps

ENV POETRY_VERSION=1.4
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR ${WORKDIR}

ENV PATH="/home/${USER}/.local/bin:${PATH}"

RUN groupadd -r ${GROUP} && useradd --no-log-init -m -r -g ${GROUP} ${USER} && \
    chown -R ${USER}:${GROUP} ${WORKDIR} \
    && chown -R ${USER}:${GROUP} /home/${USER} \
    && apt update && apt install -y build-essential && apt install -y libpq-dev && rm -rf /var/lib/apt/lists/*

FROM base as builder

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./
COPY ${SRC_CODE_DIR} .

RUN poetry config virtualenvs.in-project true && \
    poetry install --only=main --no-root 

FROM builder as final

USER ${USER}

COPY --chown=${USER}:${GROUP} ./gunicorn.conf.py .
COPY --chown=${USER}:${GROUP} --chmod=744 docker-entrypoint.sh .

CMD ["./docker-entrypoint.sh"]
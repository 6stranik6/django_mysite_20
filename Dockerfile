FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip "poetry==1.7.1"
#COPY mysite/requirements.txt requirements.txt

#RUN pip install --upgrade pip
#RUN pip install -r requirements.txt
RUN poetry config virtualenvs.create false --local
COPY poetry.lock pyproject.toml ./
RUN poetry install

COPY mysite .

CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]
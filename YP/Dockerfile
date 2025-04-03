FROM python:3.10

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# определяю корневую директорию, куда упадет проект
WORKDIR /YP

# копирую файл с зависимостями
COPY requirements.txt .

# Глобальные зависимости для запуска через менеджер процессов
RUN apt-get update && apt-get install -y nodejs npm
RUN npm install -g pm2
RUN pip install gunicorn
RUN apt-get update && apt-get install -y nano
RUN apt-get install -y nginx

# Выполняю команды, необходимые для поднятия проекта
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# RUN useradd -rms /bin/bash pm_manager

COPY . .

RUN mkdir -p /YP/static && mkdir -p /YP/media

EXPOSE 8000

CMD ["bash", "-c", "python manage.py migrate && pm2-runtime start start_django.py --interpreter python3 --name django-app"]



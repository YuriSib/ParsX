import os
from django.core.management import execute_from_command_line

print('Запускаю проект в PM2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'YP.settings')
execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])

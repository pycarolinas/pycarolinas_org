import os
import re
import datetime
import string
import json

from fabric.contrib.project import rsync_project
from fabric.contrib.files import upload_template
from fabric.api import local, run, sudo
from fabric.state import env
from fabric.context_managers import cd

dev_conf = json.load(open('dev_conf.json'))
env.hosts = ['pycarolinas.org']
env.user = dev_conf['user']
env.project_dir = '/home/pycar/pycarolinas_org'


def clean():
    local('find . -name "*.swp" -delete')

def build():
    local('lessc pycarolinas_org/static/site.less pycarolinas_org/static/site.css')

def deploy(delete=True):
    build()
    rsync_project(local_dir='pycarolinas_org', remote_dir='/home/pycar/pycarolinas_org/')
    collectstatic()
    restart_django()

def nginx_update():
    local('scp conf/pycarolinas-org.conf %s@pycarolinas.org:/etc/nginx/sites-available/' % (env.user,))
    sudo('service nginx restart')

def collectstatic():
    run('env/bin/python pycarolinas_org/manage.py collectstatic -l --noinput --settings=pycarolinas_org.settings.local')

def stop_django():
    run('kill `cat /home/pycar/django-fcgi.pid`')

def start_django():
    run('env/bin/python pycarolinas_org/manage.py runfcgi host=127.0.0.1 port=8080 pidfile=/home/pycar/django-fcgi.pid --settings=pycarolinas_org.settings.local')

def restart_django():
    stop_django()
    start_django()

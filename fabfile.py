import os
from fabric.api import *
from fabric.contrib import files
from fabric import utils
from fabtools import python
from fabric.operations import *
from fabric.context_managers import shell_env

# project settings:
env.project_name = 'kandu'
env.project_root = '~'
env.source_repo = 'https://kandu:1qaz2wsx@xp-dev.com/git/kandu'
env.user = 'narek'

env.virtualenv_path = os.path.join(env.project_root, env.project_name + '-venv')
env.code_root = os.path.join(env.project_root, env.project_name)
env.virtualenv = 'source %s/bin/activate' % env.virtualenv_path


@task
def setup(existing_server=False, database_password=None):
	env.database_password = database_password or generate_password()

	with cd(env.project_root):
		run('git clone %s %s' % (env.source_repo, env.project_name))
		with cd(env.code_root):
			if not existing_server: install_system_deps()

			if not existing_server:
				run('wget --no-check-certificate https://www.python.org/ftp/python/2.7.6/Python-2.7.6.tgz', quiet=True)
				run('tar zxvf Python-2.7.6.tgz', quiet=True)
				with cd('Python-2.7.6'):
					run('CFLAGS=-fPIC ./configure --enable-shared && make -j2', quiet=True)
					sudo('make altinstall', quiet=True)

			if not python.is_installed('virtualenv'):
				sudo('pip install virtualenv')
			run('virtualenv -p python2.7 %s' % env.virtualenv_path)

			with prefix(env.virtualenv):
				with shell_env(PATH='$PATH:/usr/pgsql-9.2/bin/'):
					run('pip install -r requirements.txt')

				if existing_server:
					if env.database_password != database_password: # need to change the password
						sudo('psql -U postgres -c "alter user kandu with password %s;"' % env.database_password)
				else:
					run('psql -U postgres -c "CREATE ROLE kandu WITH PASSWORD \'%s\' NOSUPERUSER CREATEDB NOCREATEROLE LOGIN;"' % database_password)
					run('psql -U postgres -c "CREATE DATABASE %s WITH OWNER=kandu TEMPLATE=template0 ENCODING=\'utf-8\';"' % env.project_name)
					run('psql %s -U postgres -c "CREATE EXTENSION postgis;"' % env.project_name)
					run('psql %s -U postgres -c "CREATE EXTENSION postgis_topology;"' % env.project_name)

				files.upload_template('deploy/server_config.json', './server_config.json', {'env': env})

				run('python manage.py syncdb --migrate --noinput')
				run('python manage.py collectstatic --noinput')

				if not existing_server:
					run('echo "from django.contrib.auth.models import User; User.objects.create_superuser(\'%s\', \'admin@example.com\', \'%s\')" | python manage.py shell' % (env.user, database_password))

			configure_apache(existing_server)
			run('service httpd restart')

			print 'Deployment to %s is done.\nDjango superuser has\n\tusername: %s\n\tpassword:%s' % (env.host, env.user, database_password)


@task
def update_code_on():
	with cd(env.code_root):
		run('git pull')

		with prefix(env.virtualenv):
			run('pip install -r requirements.txt')
			run('python manage.py collectstatic --noinput')

	run('service httpd restart')
	# run('touch wsgi.py')


@task
def migrate_existing_server_at(database_password=None):
	if not database_password:
		exit('Supply the current database password, please. For example, `fab migrate_existing_server_at:host=demo.kandu.co.za,database_password=EgftsDh`')

	setup(existing_server=True, database_password=database_password)


@task
def push_key_to():
    keyfile = '/tmp/%s.pub' % env.user
    run('mkdir -p ~/.ssh && chmod 700 ~/.ssh')
    put('~/.ssh/id_rsa.pub', keyfile)
    run('cat %s >> ~/.ssh/authorized_keys' % keyfile)
    run('rm %s' % keyfile)


def install_system_deps():
	with settings(warn_only = True):
		if run('yum --help').succeeded: # do we have yum?
			sudo('rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm')
			sudo('yum -y install yum-utils autoconf automake geoip httpd-devel openssl-devel.x86_64 bzip2-devel gcc g++ make')
			sudo('yumdownloader postgresql92-devel')
			sudo('rpm -ivh postgresql92-devel-9.2.8-1PGDG.rhel6.x86_64.rpm --nodeps')
			sudo('yum install hg-git.noarch')
		else: # no yum, will try apt-get
			res = sudo('apt-get -y install autoconf automake geoip httpd-devel openssl-devel gcc g++ make postgresql92-devel')
			if not res.succeeded:
				utils.abort('Looks like host %s is not supported by this script: it has neither yum or apt-get.\nApplication code is at %s, no other changes were made. Goodbye.' % (env.host, env.code_root))

def configure_apache(existing_server=False):
	if not existing_server:
		run('wget https://github.com/GrahamDumpleton/mod_wsgi/archive/3.5.tar.gz -O mod_wsgi-3.5.tar.gz', quiet=True)
		run('tar zxvf mod_wsgi-3.5.tar.gz')
		with cd('mod_wsgi-3.5'):
			sudo('./configure --with-python=%s/bin/python2.7' % env.virtualenv_path)

	files.upload_template('deploy/vhosts.conf', '/etc/httpd/conf.d/vhosts.conf', {'env': env}, user_sudo=True)


def generate_password():
	import string
	import random
	return ''.join(
		random.choice(string.letters + string.digits) 
		for _ in xrange(10)
	)
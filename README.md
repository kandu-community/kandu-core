#License

This code is released under the GPL



# Deployment

This manual assumes that one has working postgresql and apache installations.

1. Clone the code

		cd /opt
		git clone https://github.com/Kandu-community/kandu-core.git

2. Prepare the dev environment to build all necessary packages/libraries:

		rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
		yum -y install yum-utils autoconf automake geoip httpd-devel openssl-devel.x86_64 bzip2-devel gcc g++ make
		yumdownloader postgresql92-devel
		rpm -ivh postgresql92-devel-9.2.8-1PGDG.rhel6.x86_64.rpm --nodeps
		yum install hg-git.noarch

2. Install Python 2.7

		wget --no-check-certificate https://www.python.org/ftp/python/2.7.6/Python-2.7.6.tgz
		tar zxvf Python-2.7.6.tgz
		cd Python-2.7.6
		CFLAGS=-fPIC ./configure --enable-shared && make -j2
		make altinstall

2. Install the virtualenv Python package and create a virtual environment

		pip install virtualenv
		virtualenv -p python2.7 /opt/kandu-venv
		source kandu-venv/bin/activate

3. Install the required Python packages

		cd kandu
		export PATH=/usr/pgsql-9.2/bin:$PATH
		pip install -r requirements.txt

4. Install the mod_wsgi apache module

		wget https://github.com/GrahamDumpleton/mod_wsgi/archive/3.5.tar.gz -O mod_wsgi-3.5.tar.gz
		tar zxvf mod_wsgi-3.5.tar.gz
		cd mod_wsgi-3.5
		./configure --with-python=/opt/kandu-venv/bin/python2.7

5. Create a pgsql database

		su - postgres
		psql
		create role kandu login password 'kandu23jh4k3j24h';
		create database kandu owner kandu;
		^D ^D

6. Configure Django by editing kandu/settings.py:
  * in DATABASES setting, specify connection settings for your database (username, password, port, etc.)
  * set STATIC_ROOT to absoulte path to the directory which will contain static files (js, css)
  * set MEDIA_ROOT to the directiry which will contain files uploaded by users

  For more information, see https://docs.djangoproject.com/en/dev/ref/settings/

7. Create tables in the databse

		python manage.py syncdb --migrate

7. Copy static files to STATIC_ROOT directory

		python manage.py collectstatic

7. The required Apache configuration is as follows:

		LoadModule wsgi_module modules/mod_wsgi.so
		WSGIPythonPath /opt/kandu/kandu:/opt/kandu-venv/lib/python2.7/site-packages
		WSGISocketPrefix /var/run/wsgi
		<VirtualHost *:80>
			ServerName partnerfarmer.kandu.co.za
			ErrorLog  /var/log/httpd/kandu.error.log
			CustomLog /var/log/httpd/kandu.access.log combined
			WSGIScriptAlias / /opt/kandu/kandu/wsgi.py
			WSGIDaemonProcess partnerfarmer.kandu.co.za python-path=/opt/kandu:/opt/kandu-venv/lib/python2.7/site-packages/
			WSGIProcessGroup partnerfarmer.kandu.co.za
			WSGIPassAuthorization On
			Alias /static /opt/kandu-static
			Alias /media /opt/kandu-media
			<Directory /opt/kandu/kandu>
				<Files wsgi.py>
					Order deny,allow
					Allow from all
				</Files>
			 </Directory>
		</VirtualHost>

8. Don't forget to send a signal to Apache (service httpd reload) or restart it
(service httpd restart) to apply its new configuration.

Unfortunately, it's not possible to write a universal
step-by-step manual for any Linux distro/installation.
This manual has been writen for CentOS 6 installed on odk.kandu.co.za

Configure the DATABASES setting and run `python manage.py syncdb`.

In order to "file" fields to work, set MEDIA_ROOT according to your environment.

# Usage

## Creating or changing forms

Upload JSON config file at `/web/update-migrate/` (`config.json` in the root of this repo is an example of such file) or run `python manage.py config_update`.

Then perform database migration:

	python manage.py schemamigration forms --auto
	python manage.py migrate

# Notes

## API

For client app to authenticate, the token key should be included in the Authorization HTTP header. The key should be prefixed by the string literal "Token", with whitespace separating the two strings. For example:

	Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

The token may be obtained by POSTing username and password to `/api/get-token/`

API can be explored and tested through web-browser starting at `/api/`.

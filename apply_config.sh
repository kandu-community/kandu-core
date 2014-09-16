#!/bin/bash
#
#Script to be applied after making changes to config.json via the UI
#

KANDUHOME='/Users/colorfulfool/Projects/config-generated-forms/repo/'
STATE=`echo $?`

cd $KANDUHOME
source /opt/kandu-venv/bin/activate


if [ -e $KANDUHOME/forms/models.py ]
then
	rm -rf $KANDUHOME/forms/models.py
fi 

if [ -e $KANDUHOME/forms/models.pyc ]
then 
	rm -rf $KANDUHOME/forms/models.py
fi

python $KANDUHOME/manage.py config_update && python $KANDUHOME/manage.py schemamigration forms --auto && python $KANDUHOME/manage.py migrate

if [ $STATE == 0 ]
then 
	touch $KANDUHOME/kandu/wsgi.py
else
	exit 1
fi

exit 0



	
		
		


from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    # args = '<poll_id poll_id ...>'
    help = 'Updates forms to match config file'

    def handle(self, *args, **options):
        #TODO: вызвыать транслэйт

        call_command('schemamigration', 'forms --auto')
        call_command('migrate', 'forms')
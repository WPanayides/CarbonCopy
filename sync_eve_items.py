# management/commands/sync_eve_items.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from celery.schedules import crontab
from celery.task import periodic_task
from your_app.tasks import pull_items_and_store_in_db

class Command(BaseCommand):
    help = 'Sync EVE items every 15 minutes'

    def handle(self, *args, **options):
        @periodic_task(run_every=(crontab(minute='*/15')), name="sync_eve_items", ignore_result=True)
        def sync_eve_items():
            pull_items_and_store_in_db.delay()
            self.stdout.write(self.style.SUCCESS(f'EVE items synced at {timezone.now()}'))

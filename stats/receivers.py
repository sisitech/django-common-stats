rimport os

from django.db import models
from django.dispatch import receiver

from stats.models import Export
from reports.tasks import export_custom_reports
import sys


@receiver(models.signals.post_delete, sender=Export)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.post_save, sender=Export)
def on_save_export(sender, **kwargs):
    created = kwargs["created"]
    instance = kwargs["instance"]
    if created:
        if instance.is_custom:
            # Trigget the export
            if "test" in sys.argv:
                print("Running the test now")
                export_custom_reports.task_function(instance.id)
            else:
                export_custom_reports(instance.id)

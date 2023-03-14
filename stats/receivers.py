import os

from django.db import models
from django.dispatch import receiver

from stats.models import Export


@receiver(models.signals.post_delete, sender=Export)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
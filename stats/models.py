from os import path

from django.db import models

from django.utils import timezone

from django.contrib.auth import get_user_model

from mylib.my_common import MyModel
from django.conf import settings


MyUser = get_user_model()


class ImportFile(MyModel):
    name = models.CharField(max_length=45, null=True, blank=True)
    file = models.FileField(upload_to="Imports", null=True, blank=True)


class ImportSheet(MyModel):
    import_file = models.ForeignKey(ImportFile, related_name="sheets", on_delete=models.CASCADE)
    name = models.CharField(max_length=45)
    rows_count = models.FloatField(default=-1)
    imported_rows_count = models.FloatField(default=-1)


class Export(MyModel):
    EXPORT_TYPES = (
        ("C", "CSV"),
        ("P", "PDF"),
    )
    EXPORT_STATUS = (
        ("Q", "Queued"),
        ("E", "Exporting..."),
        ("P", "Preparing Download..."),
        ("F", "Failed"),
        ("D", "Click To Download"),
    )
    name = models.CharField(max_length=45, null=True, blank=True)
    title = models.CharField(max_length=45, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    status = models.CharField(choices=EXPORT_STATUS, default="Q", max_length=3)
    rows_count = models.IntegerField(default=0, editable=False)
    exported_rows_count = models.IntegerField(default=0, editable=False)
    args = models.TextField(max_length=1000, null=True, blank=True)
    type = models.CharField(choices=EXPORT_TYPES, default="C", max_length=3)
    file = models.FileField(upload_to="Exports", null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True, editable=False)
    end_time = models.DateTimeField(null=True, blank=True, editable=False)
    user = models.ForeignKey(MyUser, null=True, blank=True, on_delete=models.CASCADE)
    errors = models.TextField(max_length=2000, null=True, blank=True)
    is_custom = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("-id",)

    @property
    def download_ready(self):
        pass

    @property
    def completed_percentage(self):
        value = 0
        if self.rows_count == 0 or self.exported_rows_count == 0:
            pass
        else:
            value = 100 * float(self.exported_rows_count) / float(self.rows_count)
        # print("{} {} {}".format(self.rows_count,self.exported_rows_count,value))
        return "{:,.2f}%".format(value)

    @property
    def duration(self):
        if self.start_time is None or self.end_time is None:
            return 0
        return 1

    def start(self, rows_count):
        self.rows_count = rows_count
        self.exported_rows_count = 0
        self.status = "E"
        self.errors = ""
        self.start_time = timezone.now()
        self.save()

    def finish(self, file_path):
        self.file.name = file_path
        self.status = "D"
        self.end_time = timezone.now()
        self.save()

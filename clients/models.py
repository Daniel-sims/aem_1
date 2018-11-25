from django.db import models
import uuid


class Client(models.Model):
    client_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    customer_count = models.IntegerField(default=0)
    fully_comp_count = models.IntegerField(default=0)
    basic_cover_count = models.IntegerField(default=0)

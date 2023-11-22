from django.db import models
from users.models import User
from gist.models import Gist

class Favourite(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    gist = models.ForeignKey(Gist, on_delete=models.CASCADE, blank=True, null=True)
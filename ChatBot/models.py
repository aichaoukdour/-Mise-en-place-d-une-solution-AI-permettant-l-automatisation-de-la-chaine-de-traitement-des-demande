from django.db import models

class LoginHistory(models.Model):
    user_id = models.IntegerField()
    ip_address = models.CharField(max_length=45)  # Possible typo here
    success = models.BooleanField()
    user_agent = models.TextField()
    date_l = models.DateTimeField()
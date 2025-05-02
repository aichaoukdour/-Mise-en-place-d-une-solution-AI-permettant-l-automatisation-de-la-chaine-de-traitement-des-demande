from django.db import models

class StatusMessage(models.Model):
    status_id = models.AutoField(primary_key=True)
    name_status = models.CharField(max_length=50)

    def __str__(self):
        return self.name_status

class EmailMessage(models.Model):
    Id_message = models.CharField(max_length=255, primary_key=True)
    email_agt = models.EmailField()
    Subject = models.CharField(max_length=255)
    body_message = models.TextField()
    date_recp_message = models.DateTimeField(auto_now_add=True)
    Requete_msg = models.TextField(blank=True, null=True)
    Message_env = models.FileField(upload_to='reports/', blank=True, null=True)
    Date_env_message = models.DateTimeField(blank=True, null=True)
    status = models.ForeignKey(StatusMessage, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.Subject} - {self.status.name_status}"

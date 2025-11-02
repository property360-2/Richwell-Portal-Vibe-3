from django.db import models

class AuditTrail(models.Model):
    actor = models.ForeignKey("users.User", on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    table_name = models.CharField(max_length=100)
    record_id = models.IntegerField()
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor} - {self.action} on {self.table_name}({self.record_id})"

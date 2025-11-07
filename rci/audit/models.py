# rci/audit/models.py
from django.db import models
from django.conf import settings


class AuditTrail(models.Model):
    """Logs every major modification in the system"""
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_actions'
    )
    action = models.CharField(max_length=100, help_text="e.g. 'created', 'updated', 'deleted'")
    entity = models.CharField(max_length=100, help_text="e.g. 'Student', 'Grade', 'Section'")
    entity_id = models.BigIntegerField(null=True, blank=True)
    old_value_json = models.JSONField(null=True, blank=True)
    new_value_json = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_trail'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entity', 'entity_id']),
            models.Index(fields=['actor', 'created_at']),
        ]

    def __str__(self):
        actor_name = self.actor.username if self.actor else 'System'
        return f"{actor_name} {self.action} {self.entity} #{self.entity_id}"


class Archive(models.Model):
    """One unified archive for any entity"""
    entity = models.CharField(max_length=100, help_text="e.g. 'Students', 'Grades', 'Terms'")
    entity_id = models.BigIntegerField(null=True, blank=True)
    data_snapshot = models.JSONField(help_text="Full JSON of the original record")
    reason = models.CharField(max_length=255, blank=True, help_text="e.g. 'Graduated', 'Term Closed'")
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='archives'
    )
    archived_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'archive'
        ordering = ['-archived_at']
        indexes = [
            models.Index(fields=['entity', 'entity_id']),
            models.Index(fields=['archived_at']),
        ]

    def __str__(self):
        return f"{self.entity} #{self.entity_id} archived - {self.reason}"

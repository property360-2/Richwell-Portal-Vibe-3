# rci/settingsapp/models.py
from django.db import models
from django.conf import settings
from django.core.cache import cache


class Setting(models.Model):
    """Global system control table"""
    key_name = models.CharField(
        max_length=100,
        unique=True,
        help_text="e.g. 'admission_link_enabled'"
    )
    value_text = models.CharField(
        max_length=255,
        help_text="e.g. 'true', 'false', '30'"
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional human note"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='setting_updates'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settings'
        ordering = ['key_name']

    def __str__(self):
        return f"{self.key_name} = {self.value_text}"

    def save(self, *args, **kwargs):
        """Clear cache when setting is updated"""
        super().save(*args, **kwargs)
        cache.delete(f'setting_{self.key_name}')

    @classmethod
    def get_value(cls, key_name, default=None):
        """Get setting value with caching"""
        cache_key = f'setting_{key_name}'
        value = cache.get(cache_key)

        if value is None:
            try:
                setting = cls.objects.get(key_name=key_name)
                value = setting.value_text
                cache.set(cache_key, value, 3600)  # Cache for 1 hour
            except cls.DoesNotExist:
                value = default

        return value

    @classmethod
    def get_bool(cls, key_name, default=False):
        """Get setting as boolean"""
        value = cls.get_value(key_name, str(default))
        return value.lower() in ('true', '1', 'yes', 'on')

    @classmethod
    def get_int(cls, key_name, default=0):
        """Get setting as integer"""
        value = cls.get_value(key_name, str(default))
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @classmethod
    def get_float(cls, key_name, default=0.0):
        """Get setting as float"""
        value = cls.get_value(key_name, str(default))
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

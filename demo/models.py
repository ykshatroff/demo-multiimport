from django.db import models
from django.utils.translation import ugettext_lazy as _


class DataSource(models.Model):
    """
    A data source representation
    """
    title = models.CharField(_("title"), max_length=200)
    url = models.URLField(_("URL"), unique=True)
    poll_frequency = models.PositiveSmallIntegerField(_("poll frequency"), default=0)
    poll_count = models.PositiveIntegerField(_("number of polls"), default=0)
    last_successful_update = models.DateTimeField(_("last successful update"), blank=True, null=True)

    class Meta:
        verbose_name = _("data source")
        ordering = 'title',

    def __str__(self):
        return f'{self.title}[{self.url}]'

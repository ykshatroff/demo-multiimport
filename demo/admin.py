from demo.models import DataSource
from django.contrib.admin import register, ModelAdmin


@register(DataSource)
class DataSourceAdmin(ModelAdmin):
    readonly_fields = "last_successful_update", "poll_count"

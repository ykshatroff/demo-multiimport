from typing import Iterable, Type, List

import logging
from django.core.exceptions import ValidationError
from django.db import models


logger = logging.getLogger(__name__)


class MapperBase:
    """
    A base mapper class.

    Update a Django model from input data, honoring `exclude_fields` (list of field names)
        and applying transformations as per `transform_FIELD` method callbacks, like in this example:

            def transform_description(self, value: Any, data: dict):
                return data['description'][:100]

    (Another transformation option is based on field type, it is more generic, but requires more configuration:
        the referred model's fields and how to map input data to them)
    """
    exclude_fields = []  # type: list[str]
    unique_fields = []  # type: list[str]

    def __init__(self, model: Type[models.Model]):
        self.model = model

        self.model_fields = {
            f.name: f
            for f in model._meta.get_fields()
            if not isinstance(f, models.AutoField) and f.name not in self.exclude_fields
        }
        for field in self.unique_fields:
            if field not in self.model_fields:
                raise TypeError(f"Unknown field '{field}' in the list of unique fields")

    def process_entry(self, data: dict) -> models.Model:
        instance_params = {}
        unique_params = {}
        m2m_params = {}  # We can not directly save M2M values to the field owner object, need a separate list
        for field_name, field in self.model_fields.items():
            try:
                transform = getattr(self, f'transform_{field_name}')
            except AttributeError:
                value = self.get_value(data, field, field_name)
            else:
                value = transform(data, field)

            if value is ...:
                # let Django use default value defined in the Model
                continue

            if isinstance(field, models.ManyToManyField):
                m2m_params[field_name] = value
            elif field_name in self.unique_fields and value is not None:
                unique_params[field_name] = value
            else:
                instance_params[field_name] = value

        if unique_params:
            instance, created = self.model.objects.get_or_create(defaults=instance_params, **unique_params)
        else:
            instance = self.model.objects.create(**instance_params)

        if m2m_params:
            for field_name, values in m2m_params.items():
                related = getattr(instance, field_name)
                related.clear()
                related.add(*values)

        return instance

    def process(self, data: Iterable) -> List[models.Model]:
        """Process an iterable of entries"""
        result = []
        for i, entry in enumerate(data):
            logger.debug(f"Processing entry {i}")
            instance = self.process_entry(entry)
            result.append(instance)
        return result

    def process_string(self, text) -> List[models.Model]:
        """Abstract method: process a data string

        :param text:
        :return: entries processed
        """
        raise NotImplementedError("Please define the implementation in the subclass!")

    def get_value(self, data: dict, field: models.Field, source_field=None):
        """Get a value for a field from `data`

        :param data:
        :param field:
        :param source_field:
        :return: None, if field must be null;
                 Any, if no special treatment required,
                 Ellipsis, to omit the field completely, letting Django manage it
        """
        if isinstance(field, models.ManyToManyField):
            return ...
        if source_field is None:
            source_field = field.name
        try:
            value = data[source_field]
        except KeyError:
            if field.blank or field.default != models.NOT_PROVIDED:
                # omit field from instance parameters, let Django handle the default
                return ...
            elif field.null:
                value = None
            else:
                raise ValidationError(f"Error in input: Missing required field '{source_field}'")

        return value

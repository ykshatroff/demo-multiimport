import pytest
from django.core.exceptions import ValidationError
from django.db import models

from mapper.base import MapperBase
from tests.models import FakeModel, FakeModelWithM2M
from unittest.mock import patch, Mock

SAMPLE_DATA = [
    {
        "required_field": "test value #1",
        "renamed_field": "test value #2"
    }
]


def test_mapper_init():
    mapper_base = MapperBase(FakeModel)
    assert mapper_base.model is FakeModel
    assert list(mapper_base.model_fields.keys()) == ['required_field', 'blank_field', 'null_field', 'default_field']
    assert isinstance(mapper_base.model_fields['required_field'], models.CharField)


def test_mapper_init_exclude():
    class MapperExclude(MapperBase):
        exclude_fields = ['required_field']

    mapper_base = MapperExclude(FakeModel)
    assert mapper_base.model is FakeModel
    assert list(mapper_base.model_fields.keys()) == ['blank_field', 'null_field', 'default_field']


def test_mapper_get_value():
    mapper_base = MapperBase(FakeModel)
    sample_data = SAMPLE_DATA[0]
    value = mapper_base.get_value(sample_data, mapper_base.model_fields['required_field'])
    assert value == "test value #1"


def test_mapper_get_value_renamed_field():
    mapper_base = MapperBase(FakeModel)
    sample_data = SAMPLE_DATA[0]
    value = mapper_base.get_value(sample_data, mapper_base.model_fields['required_field'], "renamed_field")
    assert value == "test value #2"


def test_mapper_get_value_missing():
    mapper_base = MapperBase(FakeModel)
    with pytest.raises(ValidationError):
        mapper_base.get_value({}, mapper_base.model_fields['required_field'], "missing_field")


def test_mapper_get_value_missing_blank():
    mapper_base = MapperBase(FakeModel)
    value = mapper_base.get_value({}, mapper_base.model_fields['blank_field'], "missing_field")
    assert value is ...


def test_mapper_get_value_missing_default():
    mapper_base = MapperBase(FakeModel)
    value = mapper_base.get_value({}, mapper_base.model_fields['default_field'], "missing_field")
    assert value is ...


def test_mapper_get_value_missing_null():
    mapper_base = MapperBase(FakeModel)
    value = mapper_base.get_value({}, mapper_base.model_fields['null_field'], "missing_field")
    assert value is None


def test_mapper_process_string():
    mapper_base = MapperBase(FakeModel)
    with pytest.raises(NotImplementedError):
        mapper_base.process_string("test")


def test_mapper_process():
    mapper_base = MapperBase(FakeModel)
    with patch.object(mapper_base, "process_entry") as process_entry:
        process_entry.return_value = "test"
        result = mapper_base.process(SAMPLE_DATA)
        assert result == ["test"]
        assert process_entry.called_once_with(data=SAMPLE_DATA[0])


def test_mapper_process_entry():
    mapper_base = MapperBase(FakeModel)

    with patch.object(FakeModel.objects, "create") as objects_create:
        objects_create.return_value = ...
        result = mapper_base.process_entry(SAMPLE_DATA[0])
        assert result is ...
        assert objects_create.called_once_with(required_field="test value #1")


def test_mapper_process_entry_with_unique():
    mapper_base = MapperBase(FakeModel)
    mapper_base.unique_fields = ['required_field']

    with patch.object(FakeModel.objects, "get_or_create") as objects_get_or_create:
        objects_get_or_create.return_value = ..., True
        result = mapper_base.process_entry(SAMPLE_DATA[0])
        assert result is ...
        assert objects_get_or_create.called_once_with(required_field="test value #1")


def test_mapper_process_entry_with_unique_incorrect():
    class MapperUnique(MapperBase):
        unique_fields = ['wrong_field']

    with pytest.raises(TypeError):
        MapperUnique(FakeModel)


def test_mapper_process_entry_with_transform():
    mapper_base = MapperBase(FakeModel)
    mapper_base.transform_required_field = lambda data, field: "transformed value #1"

    with patch.object(FakeModel.objects, "create") as objects_create:
        objects_create.return_value = ...
        result = mapper_base.process_entry(SAMPLE_DATA[0])
        assert result is ...
        assert objects_create.called_once_with(required_field="transformed value #1")


def test_mapper_process_entry_with_m2m():
    """Mapper skips M2M fields by default"""
    mapper_base = MapperBase(FakeModelWithM2M)

    with patch.object(FakeModelWithM2M.objects, "create") as objects_create:
        mapper_base.process_entry(SAMPLE_DATA[0])
        assert objects_create.called_once_with(required_field="transformed value #1")


def test_mapper_process_entry_with_m2m_transform():
    mapper_base = MapperBase(FakeModelWithM2M)
    mapper_base.transform_m2m_field = Mock(return_value=[...])

    with patch.object(FakeModelWithM2M, "m2m_field") as m2m_field, \
            patch.object(FakeModelWithM2M.objects, "create") as objects_create:
        result = mapper_base.process_entry(SAMPLE_DATA[0])
        assert mapper_base.transform_m2m_field.called
        assert result.m2m_field.clear.called
        assert result.m2m_field.add.called_once_with(...)

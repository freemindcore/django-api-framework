from easy.conf.settings import (
    CRUD_API_ENABLED_ALL_APPS,
    CRUD_API_EXCLUDE_APPS,
    CRUD_API_INCLUDE_APPS,
)


def test_change_django_settings(settings):
    assert settings.CRUD_API_ENABLED_ALL_APPS == CRUD_API_ENABLED_ALL_APPS
    assert settings.CRUD_API_INCLUDE_APPS == CRUD_API_INCLUDE_APPS
    assert settings.CRUD_API_EXCLUDE_APPS == CRUD_API_EXCLUDE_APPS

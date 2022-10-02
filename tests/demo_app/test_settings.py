from easy.conf.settings import (
    AUTO_ADMIN_ENABLED_ALL_APPS,
    AUTO_ADMIN_EXCLUDE_APPS,
    AUTO_ADMIN_INCLUDE_APPS,
)


def test_change_django_settings(settings):
    assert settings.AUTO_ADMIN_ENABLED_ALL_APPS == AUTO_ADMIN_ENABLED_ALL_APPS
    assert settings.AUTO_ADMIN_INCLUDE_APPS == AUTO_ADMIN_INCLUDE_APPS
    assert settings.AUTO_ADMIN_EXCLUDE_APPS == AUTO_ADMIN_EXCLUDE_APPS

from functools import lru_cache

from settings import APISettings


@lru_cache()
def get_settings() -> APISettings:
    return APISettings()
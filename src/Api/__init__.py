from Config import getConfig
from importlib import import_module


def _translate(query: str) -> str:
    return query


translate = _translate
APISetting = getConfig("Setting", "API")
if APISetting:
    try:
        translate = import_module(f"Api.{APISetting}").translate
    except Exception:
        pass

__all__ = ["translate"]

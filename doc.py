from fastapi.openapi.utils import get_openapi

from enum import Enum


class Palette(str, Enum):
    sepia = "sepia"
    wedge = "wedge"
    random = "random"
    negative = "negative"


def init_doc(app):
    openapi_schema = get_openapi(
        title="Small TIFF API",
        version="1.0",
        description="Small API built with FastAPI to retrieve and do some operations on TIFF images.",
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema

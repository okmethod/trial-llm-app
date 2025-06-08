from pydantic import BaseModel


class ImageBytes(BaseModel):
    image_key: str
    content_type: str
    data: bytes

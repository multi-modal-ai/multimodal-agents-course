import base64
import io

from PIL import Image
from pydantic import BaseModel, field_validator


class Base64ToPILImageModel(BaseModel):
    image: str

    @field_validator("image", mode="before")
    def decode_image(cls, v):
        if isinstance(v, Image.Image):
            buffered = io.BytesIO()
            v.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        return v

    def get_image(self) -> Image.Image:
        img_bytes = base64.b64decode(self.image)
        return Image.open(io.BytesIO(img_bytes))

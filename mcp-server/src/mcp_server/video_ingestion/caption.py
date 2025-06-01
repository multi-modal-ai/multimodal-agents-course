import base64
from io import BytesIO

from groq import Groq
from PIL import Image

from mcp_server.config import settings


def encode_image(image: str | Image.Image) -> str:
    """Encode an image to base64 string.

    Args:
        image (Union[str, Image.Image]): Either a file path to an image or a PIL Image object

    Returns:
        str: Base64 encoded string representation of the image

    Raises:
        FileNotFoundError: If the image path does not exist
        IOError: If there are issues reading or processing the image
    """
    try:
        if isinstance(image, str):
            with open(image, "rb") as image_file:
                image_str = image_file.read()
        else:
            if not image.format:
                image_format = "JPEG"
            else:
                image_format = image.format

            buffered = BytesIO()
            image.save(buffered, format=image_format)
            image_str = buffered.getvalue()

        return base64.b64encode(image_str).decode("utf-8")

    except (FileNotFoundError, IOError) as e:
        raise IOError(f"Failed to process image: {str(e)}")


class VisualCaptioningModel:
    """A model for generating captions from images using Groq's vision-language models.

    This class provides functionality to caption images using Groq's VLM models through their API.

    Args:
        model_name (str): The name of the Groq model to use. Defaults to settings.GROQ_VLM_MODEL.

    Attributes:
        model_name (str): The name of the Groq model being used.
        client (Groq): The Groq API client instance.
    """

    def __init__(self, model_name: str = settings.GROQ_VLM_MODEL):
        self.model_name = model_name
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def caption(self, image: Image.Image | str, prompt: str) -> str:
        """Generate a caption for the given image using the specified prompt.

        Args:
            image (Union[Image, str]): The input image, either as a PIL Image object or a path string.
            prompt (str): The prompt text to guide the caption generation.

        Returns:
            str: The generated caption text.

        Note:
            If image is provided as a string, it will be loaded and converted to RGB format.
        """
        base64_image = encode_image(image)

        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            model=self.model_name,
        )
        return chat_completion.choices[0].message.content

    def __repr__(self):
        return f"VisualCaptioningModel(model_name={self.model_name})"

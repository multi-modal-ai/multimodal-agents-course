import time
from pathlib import Path
from typing import Any, List, Tuple

from PIL.Image import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

from services.perception_models.apps.plm.generate import (
    PackedCausalTransformerGenerator,
    PackedCausalTransformerGeneratorArgs,
    dataclass_from_dict,
    get_image_transform,
    get_video_transform,
    load_consolidated_model_and_tokenizer,
)

# TEMPORARY
# move to server ?


class CaptioningModel:
    def __init__(self, device: str = "cuda", pretext: str = "a photography of"):
        self._model_tag = "Salesforce/blip-image-captioning-base"
        self._device = device
        self._pretext = pretext

        self.model = BlipForConditionalGeneration.from_pretrained(self._model_tag, device_map="auto")
        self.processor = BlipProcessor.from_pretrained(self._model_tag)
        self.model.to(device)

    def __call__(self, image_frame) -> str:
        inputs = self.processor(image_frame, self._pretext, return_tensors="pt").to(self._device)
        out = self.model.generate(**inputs)
        caption = self.processor.decode(out[0], skip_special_tokens=True)
        del inputs, out
        return caption

    def __repr__(self):
        return f"CaptioningModel(model_tag={self._model_tag}, device={self.device})"


class VisualCaptioningModel:
    def __init__(self, device: str = "cuda"):
        self._model_tag = "facebook/Perception-LM-3B"
        self.model_dir = (
            Path("/home/razvantalexandru/Documents/Projects/NeuralBits/multimodal-agents-course/services/checkpoints")
            / self._model_tag
        )
        self._device = device
        model, tokenizer, config = load_consolidated_model_and_tokenizer(self.model_dir)

        self.image_transform = get_image_transform(
            vision_input_type=config.data.vision_input_type,
            image_res=model.vision_model.image_size,
            max_num_tiles=config.data.max_num_tiles,
        )

        self.video_transform = get_video_transform(image_res=model.vision_model.image_size)
        self.max_frames = config.data.max_video_frames

        generation_cfg = dataclass_from_dict(PackedCausalTransformerGeneratorArgs, {}, strict=False)
        self.generator = PackedCausalTransformerGenerator(generation_cfg, model, tokenizer)

    def preprocess_image(self, frames_set: List[Image], prompt: str):
        images = [self.image_transform(image)[0] for image in frames_set]
        return [(prompt, images)]

    def preprocess_video(self, video_path: Path, prompt: str):
        video_info = (video_path, self.max_frames, None, None, None)
        frames, _ = self.video_transform(video_info)
        return [(prompt, frames)]

    def __call__(self, inputs: List[Tuple[Any, str]]) -> str:
        generation, loglikelihood, greedy = self.generator.generate(inputs)
        return generation

    def __repr__(self):
        return f"VideoCaptionModel(model_tag={self._model_tag}, device={self.device})"

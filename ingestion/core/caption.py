import os
from enum import Enum
from pathlib import Path

import torch
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration


class CaptionModelType(str, Enum):
    Qwen25_3B = "QwenVL2.5-3B"


DEFAULT_MODEL_CHECKPOINTS_DIR = Path(os.getcwd()) / "checkpoints"
DEFAULT_MODEL_REGISTRY = {
    CaptionModelType.Qwen25_3B: "Qwen2.5-VL-3B-Instruct",
}


def solve_device(device: str) -> str:
    if device == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    elif device == "mps" and torch.backends.mps.is_available():
        return torch.device("mps")
    else:
        return torch.device("cpu")


class VisualCaptioningModel:
    def __init__(self, device: str = "cuda", model_tag: CaptionModelType = None):
        self._model_tag = model_tag if model_tag else CaptionModelType.PLM_1B
        self.model_dir = DEFAULT_MODEL_CHECKPOINTS_DIR / DEFAULT_MODEL_REGISTRY.get(self._model_tag)
        self._device = solve_device(device)

        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            self._model_tag, torch_dtype=torch.bfloat16, device_map="auto", pretrained_model_name_or_path=self.model_dir
        )

        self.processor = AutoProcessor.from_pretrained(self._model_tag, pretrained_model_name_or_path=self.model_dir)

    def preprocess_video(self, clip_path: Path, prompt: str) -> torch.Tensor:
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "video",
                        "video": f"{str(clip_path)}",
                        "max_pixels": 360 * 420,
                        "fps": 1.0,
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs, video_kwargs = process_vision_info(messages, return_video_kwargs=True)
        inputs: torch.Tensor = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            fps=1,
            padding=True,
            return_tensors="pt",
            **video_kwargs,
        )
        inputs = inputs.to(self.device)
        return inputs

    def infer(self, inputs: torch.Tensor, max_new_tokens: int, skip_special_tokens: bool = True) -> str:
        generated_ids = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        generated_ids_trimmed = [out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=skip_special_tokens, clean_up_tokenization_spaces=False
        )

        return output_text

    def __repr__(self):
        return f"VideoCaptionModel(model_tag={self._model_tag}, device={self.device})"

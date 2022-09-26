from typing import Iterator, Type

from tortoise import Model, Tortoise


def get_all_models() -> Iterator[Type[Model]]:  # fixme:需要测试
    """
    get all tortoise models
    """
    for tortoise_app, models in Tortoise.apps.items():
        for model_item, model in models.items():
            yield model


def get_model_from_str(model_name: str, app_label: str = "fast_tmp") -> Type[Model]:
    s = model_name.split(".")
    if len(s) == 2:
        app_label, model_name = s
    for tortoise_app, models in Tortoise.apps.items():
        if tortoise_app == app_label:
            for name, model in models.items():
                if model_name == name:
                    return model
    else:
        raise Exception(f"Can not found {model_name}!")

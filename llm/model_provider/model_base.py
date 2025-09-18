from settings import settings

model_providers = {
    "openai": {
        "api_base": settings.openai_api_base,
        "api_key": settings.openai_api_key,
        "default_model": "gpt-4o-mini",
    },
    "qwen": {
        "api_base": settings.qwen_api_base,
        "api_key": settings.qwen_api_key,
        "default_model": "qwen-plus",
    },
    "vol": {
        "api_base": settings.vol_api_base,
        "api_key": settings.vol_api_key,
        "default_model": settings.vol_model_endpoint,
    },
}

class ModelBase:
    def __init__(self, sel_model: str = None, **kwargs):
        if sel_model is None:
            sel_model = settings.sel_model_provider
        self.model_settings = model_providers[sel_model.lower()]
        self.top_p = kwargs.get("top_p", 0.8)
        self.temperature = kwargs.get("temperature", 0.8)

    @staticmethod
    def instance(sel_model: str = None) -> "ModelBase":
        return ModelBase(sel_model)
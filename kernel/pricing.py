from dataclasses import dataclass
from typing import Dict


# =========================
# Core pricing data model
# =========================

@dataclass(frozen=True)
class ModelPricing:
    provider: str
    model: str
    input_price_per_m: float    # USD per 1M input tokens
    output_price_per_m: float   # USD per 1M output tokens


# =========================
# OpenAI – official pricing
# Source: https://openai.com/api/pricing/
# =========================

OPENAI_PRICING: Dict[str, ModelPricing] = {
    # GPT-5 family
    "gpt-5.2": ModelPricing("openai", "gpt-5.2", 1.75, 14.00),
    "gpt-5.1": ModelPricing("openai", "gpt-5.1", 1.25, 10.00),
    "gpt-5":   ModelPricing("openai", "gpt-5",   1.25, 10.00),
    "gpt-5-mini": ModelPricing("openai", "gpt-5-mini", 0.25, 2.00),
    "gpt-5-nano": ModelPricing("openai", "gpt-5-nano", 0.05, 0.40),

    # GPT-4.x family
    "gpt-4.1": ModelPricing("openai", "gpt-4.1", 2.00, 8.00),
    "gpt-4.1-mini": ModelPricing("openai", "gpt-4.1-mini", 0.40, 1.60),
    "gpt-4.1-nano": ModelPricing("openai", "gpt-4.1-nano", 0.10, 0.40),

    # GPT-4o family
    "gpt-4o": ModelPricing("openai", "gpt-4o", 2.50, 10.00),
    "gpt-4o-mini": ModelPricing("openai", "gpt-4o-mini", 0.15, 0.60),

    # Realtime (text tokens only)
    "gpt-realtime": ModelPricing("openai", "gpt-realtime", 4.00, 16.00),
    "gpt-realtime-mini": ModelPricing("openai", "gpt-realtime-mini", 0.60, 2.40),
}


# =========================
# Gemini – official pricing
# Source: https://ai.google.dev/gemini-api/docs/pricing
# (text models only)
# =========================

GEMINI_PRICING: Dict[str, ModelPricing] = {
    # Gemini 2.5
    "gemini-2.5-flash-lite": ModelPricing(
        "gemini", "gemini-2.5-flash-lite", 0.10, 0.40
    ),
    "gemini-2.5-flash": ModelPricing(
        "gemini", "gemini-2.5-flash", 0.30, 2.50
    ),
    "gemini-2.5-pro": ModelPricing(
        "gemini", "gemini-2.5-pro", 3.50, 10.50
    ),

    # Gemini 3
    "gemini-3-flash": ModelPricing(
        "gemini", "gemini-3-flash", 0.50, 3.00
    ),
    "gemini-3-pro": ModelPricing(
        "gemini", "gemini-3-pro", 7.00, 21.00
    ),
}


# =========================
# Combined registry
# =========================

PRICING_REGISTRY: Dict[str, ModelPricing] = {}
PRICING_REGISTRY.update(OPENAI_PRICING)
PRICING_REGISTRY.update(GEMINI_PRICING)


# =========================
# Public API
# =========================

def get_model_pricing(model_name: str) -> ModelPricing:
    """
    Lookup pricing for a model.
    Only models with official published pricing are allowed.
    """
    try:
        return PRICING_REGISTRY[model_name]
    except KeyError:
        raise ValueError(
            f"Model '{model_name}' has no official published pricing "
            f"and cannot be used in agentix."
        )


def compute_cost_usd(
    model_name: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """
    Compute exact USD cost for a model call based on token usage.
    """
    pricing = get_model_pricing(model_name)
    return (
        pricing.input_price_per_m  * (input_tokens / 1_000_000) +
        pricing.output_price_per_m * (output_tokens / 1_000_000)
    )

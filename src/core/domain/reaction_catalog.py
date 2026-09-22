from __future__ import annotations

from collections.abc import Mapping

# Catalog ids from reactions.v1 — do not rename.
REACTION_LAYER: Mapping[str, str] = {
    "acknowledge": "emotional",
    "support": "emotional",
    "empathy": "emotional",
    "concern": "emotional",
    "hopeful": "emotional",
    "sad": "emotional",
    "outraged_situation": "emotional",
    "amused": "emotional",
    "agree": "epistemic",
    "disagree": "epistemic",
    "useful_fact": "epistemic",
    "insightful": "epistemic",
    "needs_evidence": "epistemic",
    "off_topic": "moderation",
    "aggressive": "moderation",
}

CATALOG_REACTION_IDS = frozenset(REACTION_LAYER)
MODERATION_REACTION_IDS = frozenset(
    reaction_id for reaction_id, layer in REACTION_LAYER.items() if layer == "moderation"
)
MUTEX_PAIRS = {"agree": "disagree", "disagree": "agree"}


def layer_for(reaction_id: str) -> str | None:
    """Return catalog layer or None if reaction_id is not in reactions.v1."""
    return REACTION_LAYER.get(reaction_id)

"""Resolve the language used for generated book labels."""

SUPPORTED_BOOK_LANGUAGES = ("fr", "en")


def resolve_book_language(
    requested_language: str | None,
    *,
    gramps_language: str | None = None,
) -> str:
    """Return a supported base language, falling back to English deterministically."""
    requested = (requested_language or "").strip().casefold()
    if not requested or requested == "auto":
        requested = (gramps_language or "").strip().casefold()

    base_language = requested.replace("_", "-").split("-", 1)[0]
    return base_language if base_language in SUPPORTED_BOOK_LANGUAGES else "en"


def model_book_language(model, *, default: str = "fr") -> str:
    """Get the output language from metadata or a renderer's legacy default."""
    metadata = getattr(model, "metadata", {}) or {}
    configured = metadata.get("BOOK_LANGUAGE")
    if configured is None:
        return default
    return resolve_book_language(configured)

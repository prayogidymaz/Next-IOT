"""Jinja2 templates for rule actions (StrictUndefined)."""

from __future__ import annotations

from jinja2 import Environment, StrictUndefined, TemplateSyntaxError, UndefinedError

_jinja_env = Environment(undefined=StrictUndefined, autoescape=False)


def compile_template(template: str) -> None:
    """Raise TemplateSyntaxError if template is invalid."""
    _jinja_env.from_string(template)


def render_template(template: str, context: dict[str, object]) -> str:
    try:
        return _jinja_env.from_string(template).render(**context)
    except UndefinedError as exc:
        raise ValueError(f"Template variable missing: {exc}") from exc


def validate_template_string(template: str) -> str | None:
    try:
        compile_template(template)
    except TemplateSyntaxError as exc:
        return str(exc)
    return None

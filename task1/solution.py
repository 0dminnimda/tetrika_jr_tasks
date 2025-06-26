import sys
import functools
import inspect
import types
import typing
from typing import Callable, Any


def _format_type(type_hint: Any) -> str:
    """Format a type annotation into a readable string"""

    # int | str, (Python 3.10+)
    if sys.version_info >= (3, 10) and isinstance(type_hint, types.UnionType):
        return str(type_hint)

    # typing.Union and other generics (List[int], etc.)
    if hasattr(type_hint, '_name') or typing.get_origin(type_hint) is not None:
         return str(type_hint)

    # simple types
    if hasattr(type_hint, '__name__'):
        return type_hint.__name__

    return str(type_hint)


def strict(func: Callable) -> Callable:
    """Add runtime argument type checking"""

    # Let's assume function will not be tempered with in runtime
    signature = inspect.signature(func)
    type_hints = None

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        nonlocal type_hints
        if type_hints is None:
            try:
                # Resolve string annotations 'str' => str
                type_hints = typing.get_type_hints(func)
            except NameError:
                raise NameError(f"Cannot resolve type hints for '{func.__name__}'. "
                                f"Make sure all forward-referenced types are defined.")

        bound_args = signature.bind(*args, **kwargs).arguments

        for name, value in bound_args.items():
            annotation = type_hints.get(name)
            if annotation is None:
                continue

            if not isinstance(value, annotation):
                raise TypeError(
                    f"argument '{name}' must be of type "
                    f"'{_format_type(annotation)}', but got '{type(value).__name__}'"
                )

        return func(*args, **kwargs)

    return wrapper

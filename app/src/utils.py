import inspect
from functools import wraps
from typing import Callable, Awaitable, Any, Union, Iterable


def depends_decorator(
        **decorator_kwargs: Union[
            Callable[[], Awaitable[Any]],
            Callable[[], Any],
            tuple[Awaitable[Any], Iterable, dict],
            tuple[Callable[[Any], Any], Iterable, dict],

        ]):
    def func_wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            inner_kwargs = {}
            for key in decorator_kwargs:
                value = decorator_kwargs[key]
                if isinstance(value, tuple):
                    result = value[0](*value[1], **value[2])
                else:
                    result = value()
                if inspect.isawaitable(result):
                    result = await result
                inner_kwargs[key] = result
            return await func(*args, **kwargs, **inner_kwargs)

        return inner

    return func_wrapper

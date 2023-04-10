import datetime as dt
import inspect
from functools import wraps
from typing import Any, Awaitable, Callable, Iterable, Union

from arq import ArqRedis, Retry


def depends_decorator(
    **decorator_kwargs: Union[
        Callable[[], Awaitable[Any]],
        Callable[[], Any],
        tuple[Callable[[Any], Any], Iterable, dict],
    ]
):
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


async def run_kinda_async_task(arq_poll: ArqRedis, *args, **kwargs) -> Any:
    job = await arq_poll.enqueue_job(*args, **kwargs)
    if job is None:
        raise Exception("Не удалось запустить задачу.")
    return await job.result()


def retry_(
    defer_: Union[dt.timedelta, int] = dt.timedelta(seconds=5),
    max_tries: int = 1,
):
    def func_wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if args[0]["job_try"] == max_tries:
                    raise e from e
                raise Retry(defer=defer_) from e

        return inner

    return func_wrapper

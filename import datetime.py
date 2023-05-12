import datetime
import backoff


@backoff.on_exception(
    wait_gen=backoff.constant,
    exception=Exception,
    max_tries=5,
    interval=1,
    jitter=None,
)
def test(starttime: datetime.datetime) -> None:
    print(f"time:{starttime - datetime.datetime.now()}")
    raise Exception("ошибка")


@backoff.on_exception(
    wait_gen=backoff.expo,
    exception=Exception,
    max_tries=5,
)
def test2(starttime: datetime.datetime) -> None:
    print(f"time:{datetime.datetime.now()-starttime}")
    raise Exception("ошибка")


# test(datetime.datetime.now())
# test2(datetime.datetime.now())


class B:
    b1 = 1
    b2 = 2


class A:
    a = 1
    b = B()


a = A()

# print(hasattr(a, "c"))
# b = getattr(a, "c")
# print(b.b2)


d1 = {"11": 11, "12": 12}
d2 = {"21": 21, "22": 22, "12": 23}
d2.update(d1)

print(d2)

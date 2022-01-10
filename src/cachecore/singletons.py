from functools import cache


def singleton(class_):
    class_.__new__ = cache(class_.__new__)
    return class_


@singleton
class MissingKeyType:

    def __bool__(self):
        return False

    def __repr__(self):
        return 'MissingKey'


@singleton
class DefaultType:

    def __repr__(self):
        return 'Default'


MissingKey = MissingKeyType()
Default = DefaultType()
class Context:
    __abstract__ = True

    cost = 1
    transparent = False

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self, *args):
        raise NotImplementedError()

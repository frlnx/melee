from unittest.mock import MagicMock


class FakeFactory(object):
    model_view_map = {}

    def manufacture(self, *args, **kwargs):
        mm = MagicMock()
        return mm

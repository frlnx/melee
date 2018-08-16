from unittest.mock import MagicMock


class FakeFactory(object):
    def manufacture(self, name, view_class=None, sub_view_class=None):
        return MagicMock()

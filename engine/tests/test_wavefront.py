from engine.views.wavefront_parsers import ObjectParser


with open("objects/cockpit.obj", 'r') as f:
    object_file_data = f.readlines()


class TestIntegratingObjectParser(object):

    def setup(self):
        self.parser = ObjectParser()
        self.target = self.parser.parse(object_file_data)

    def test_object_has_faces(self):
        assert len(self.target._faces) > 0

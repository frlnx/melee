from engine.models.factories import ShipModelFactory
from engine.tests.fake_view_factory import FakeFactory
from engine.views import menus


class TestBaseMenu(object):

    def setup(self):

        def test_func():
            pass

        self.target = menus.BaseMenu.labeled_menu_from_function_names("test", [test_func], 0, 0)

    def test_menu_has_a_button(self):
        assert len(self.target.buttons) == 1


class TestInputMenu(object):

    def setup(self):

        def arg_func(name: str="foo", age: int=8000):
            pass

        def cancel_func():
            pass

        self.target = menus.InputMenu.input_menu("test", arg_func, 0, 0, cancel_func, 36)

    def test_menu_has_two_input_fields(self):
        assert len(self.target.inputboxes) == 2

    def test_menu_func_is_callable(self):
        self.target.buttons[0].func()


class TestConfigControlsMenu(object):
    smf = ShipModelFactory()
    def setup(self):
        self.ship_model = self.smf.manufacture("ship")
        def cancel_func():
            pass

        fake_mesh_factory = FakeFactory()
        self.target = menus.ControlConfigMenu.manufacture_for_ship_model(self.ship_model, cancel_func, 0, 0,
                                                                        fake_mesh_factory)

    def test_menu_has_two_button(self):
        assert len(self.target.buttons) >= 2

import pickle


def get_factory():
    with open('meshfactory.pkl', 'rb') as f:
        mesh_factory = pickle.load(f)
    return mesh_factory


def cached_factory(mesh_factory):
    def f():
        return mesh_factory
    return f


factory = get_factory()
get_factory = cached_factory(factory)

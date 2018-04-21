#!python
import pickle
from os import path, listdir

from engine.views.opengl_mesh import OpenGLWaveFrontFactory

if __name__ == "__main__":
    files = [path.join("objects", file_name) for file_name in listdir('objects') if file_name.endswith('.obj')]
    f = OpenGLWaveFrontFactory(files)
    with open('meshfactory.pkl', 'wb') as p:
        pickle.dump(f, p)

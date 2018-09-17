from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules = cythonize('form_conv_cy.pyx'))

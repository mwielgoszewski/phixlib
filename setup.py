# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools.extension import Extension


try:
    from Cython.Build import cythonize
except ImportError:
    USE_CYTHON = False
else:
    USE_CYTHON = True


ext = '.pyx' if USE_CYTHON else '.c'

extensions = [Extension('phixlib.parser', ['phixlib/parser' + ext])]


if USE_CYTHON:
    extensions = cythonize(extensions)


setup(
    name='phixlib',
    version='1.0',
    author='Marcin Wielgoszewski',
    packages=['phixlib'],
    package_data={
        'phixlib': ['spec/*.xml', 'spec/*.json'],
    },
    ext_modules=extensions,
    zip_safe=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: C',
        'Programming Language :: Cython',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development',
    ],
)

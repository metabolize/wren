version = '0.3.5'

# https://coderwall.com/p/qawuyq
# Thanks James.

try:
   import pypandoc
   long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError, RuntimeError):
   long_description = ''

import os
requirements_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'requirements.txt')

with open(requirements_file, 'r') as f:
    install_requires = [x.strip() for x in f.readlines()]

from setuptools import setup

setup(
    name='wren',
    version=version,
    author='Body Labs',
    author_email='paul.melnikow@bodylabs.com',
    description='Synchronous RESTful API consumer based on Requests',
    long_description=long_description,
    url='https://github.com/bodylabs/wren',
    license='Apache 2',
    packages=[
        'wren',
    ],
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

#!/usr/bin/env python

import unittest
from setuptools import find_packages, setup, dist

sphinx_deps = ['Sphinx==3.4.3']
dist.Distribution().fetch_build_eggs(sphinx_deps)
from sphinx.setup_command import BuildDoc


name = 'SMARTSexplore'
version = '1.0'
release = '1.0.0'
author = 'Inken Fender, Pia Plümer, Simon Welker'


python_requires='>=3.8',


cmdclass = {
    'build_sphinx': BuildDoc
}
command_options = {
    'build_sphinx': {
        'project': ('setup.py', name),
        'version': ('setup.py', version),
        'release': ('setup.py', release),
        'source_dir': ('setup.py', 'docs')
    }
}


setup(
    name=name,
    author=author,
    version=version,
    packages=find_packages(),
    install_requires=[
        'Flask==1.1.2',             # the web framework we use
        'Werkzeug==1.0.1',          # (making Flask's dependency explicit)
        'python-dotenv==0.15.0',    # for recognizing the Flask app when running `flask` on console
        'flask-compress==1.8.0',    # for sending gzipped responses from the backend
        'click==7.1.2',             # for backend management commands
        'tqdm==4.51.0',             # for progress bars of backend management commands

        'sqlalchemy==1.3.20',       # our database layer

        'pytest==6.2.2',            # our testing framework
        'pytest-cov==2.11.1',       # for generating coverage from pytest
        'selenium'         # for end-to-end tests
    ] + sphinx_deps + [             # our documentation generator
        'sphinx_rtd_theme==0.5.1',  # for styling the documentation HTML output like readthedocs.io
        'recommonmark==0.7.1',      # for using Markdown in the documentation (esp. for the guides)
        'sphinx-js==0.0.1337'       # for generating Sphinx docs from JS source code -- note that
                                    # this is an officially inexistent version, to force setuptools
                                    # to use our own fork of the package (see dependency_links)
    ],
    dependency_links=[
        'git+https://github.com/cobalamin/sphinx-js.git@0.0.1337#egg=sphinx-js-0.0.1337'
    ],
    cmdclass=cmdclass,
    command_options=command_options,
)





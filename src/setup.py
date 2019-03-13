try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import prompt

config = {
    'description': 'Prompts for data',
    'author': 'Johannes C. Hofmeister',
    'url': '',
    'download_url': '',
    'author_email': 'py_prompt@spam.cessor.de',
    'version': prompt.__version__,
    'tests_require': ['nose', 'kazookid'],
    'packages': ['prompt'],
    'scripts': [],
    'name': 'prompt'
}

setup(**config)
from setuptools import setup, find_packages

from pipobot import __version__

setup(
    name = 'pipobot',
    version = __version__,
    description = 'A modular bot for Jabber MUCs',
    author = 'Pipoteam',
    author_email = 'pipoteam@xouillet.info',
#   url = '',

    packages = find_packages(exclude=["modules*"]),
#   data_files = [],
#   scripts = [],

    entry_points = {
        'console_scripts' : [
            'pipobot = pipobot.bot:main',
        ]
    },

    install_requires=['distribute'],
    requires=['BeautifulSoup'],
)

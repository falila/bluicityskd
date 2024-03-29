"""Minimal setup file for tasks project."""

from setuptools import setup, find_packages

setup(
    name='blu',
    version='0.1.0',
    license='proprietary',
    description='Bluicity',

    author='Raphael KEITA',
    author_email='falila.basket@gmail.com',
    url='',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    install_requires=['click', 'requests', 'pathlib', 'psycopg2','SQLAlchemy','imap-tools',''],

    entry_points={
        'console_scripts': [
            'blu = blu.main_worker:main',
        ]
    },
)

from setuptools import setup, find_packages

from version import __version__

setup(
    name='flask-pack',
    version=__version__,
    packages=find_packages(),
    url='https://github.com/stan5079/flask-pack',
    license='GNU General Public License v3.0',
    author='Stan Mertens',
    description='A Flask extension to bundle CSS and JS files.',
    python_requires='>=3.10',
    install_requires=[
        'flask>=2.0.0',
        'beautifulsoup4>=4.0.0',
        'jinja2>=3.0.0',
        'rjsmin>=1.2.1'
    ]
)

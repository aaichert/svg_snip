from setuptools import setup, find_packages

setup(
    name='svg_snip',
    version='1.0.0',
    author='Andre Aichert',
    author_email='aaichert@gmail.com',
    description='Generate simple SVG snippets for use in Jupyter.',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'IPython'
    ],
)
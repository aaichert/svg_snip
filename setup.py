from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='svg_snip',
    version='1.0.0',
    author='Andre Aichert',
    author_email='aaichert@gmail.com',
    description='Generate simple SVG snippets for use in Jupyter.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aaichert/svg_snip",
    project_urls={
        "Bug Tracker": "https://github.com/aaichert/svg_snip/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        'numpy',
        'IPython'
    ],
    keywords="svg, jupyter, visualization, graphics",
)
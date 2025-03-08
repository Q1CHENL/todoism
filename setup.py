from setuptools import setup, find_packages
import pathlib

# Get the long description from the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='todoism',
    version='1.21.2',
    packages=find_packages(exclude=['test']),
    package_dir={'todoism': 'todoism'},
    entry_points={
        'console_scripts': [
            'todo=todoism.main:run',
            'todoism=todoism.main:run',
        ],
    },
    install_requires=[],
    author='Qichen Liu',
    author_email='liuqichne@email.com',
    description='A simple and easy-to-use todo TUI',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Q1CHENL/todoism',
    project_urls={
        "Bug Tracker": "https://github.com/Q1CHENL/todoism/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    license="MIT",
)

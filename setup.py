from setuptools import setup, find_packages

setup(
    name='todoism',
    version='1.12',
    packages=find_packages(exclude=['test']),
    package_dir={'todoism': 'todoism'},
    entry_points={
        'console_scripts': [
            'todo=todoism.main:main',
            'todoism=todoism.main:main',
        ],
    },
    install_requires=[],
    author='Qichen Liu',
    author_email='liuqichne@email.com',
    description='A simple but interactive and intuitive todo CLI',
    url='https://github.com/Q1CHENL/todoism',
)

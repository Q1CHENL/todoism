from setuptools import setup, find_packages

setup(
    name='todoism',
    version='1.16',
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
    description='A simple but interactive and intuitive todo CLI',
    url='https://github.com/Q1CHENL/todoism',
)

from setuptools import find_packages, setup

setup(
    name='metadata',
    version='0.0.1',
    packages=find_packages(),
    install_requires=['flask', 'click', 'pymongo'],
    entry_points={
        'console_scripts': [
            'metadata=metadata.cli:main',
        ],
    },
)

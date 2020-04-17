from setuptools import find_packages, setup

with open('README.md', encoding='utf8') as f:
    readme = f.read()

setup(
    name='MyMetadata',
    version='0.0.1',
    license='BSD',
    maintainer='Sunshine',
    maintainer_email='sunshineplan@gmail.com',
    description='My Metadata',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['flask', 'pymongo'],
)

from setuptools import setup, find_packages

setup(
    name="umea",
    version="0.3b",
    install_requires=[
        "python-ldap",
    ],
    description=('Python LDAP ORM'),
    packages=find_packages(exclude=['tests']),
)

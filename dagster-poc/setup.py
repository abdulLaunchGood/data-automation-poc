from setuptools import find_packages, setup

setup(
    name="dagster_poc",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "dagster",
        "dagster-webserver",
        "pandas",
        "requests",
    ],
    extras_require={
        "dev": []
    },
)

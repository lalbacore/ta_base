from setuptools import setup, find_packages

setup(
    name="team-agent",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "python-dateutil>=2.8.2",
        "requests>=2.31.0",
    ],
    python_requires=">=3.11",
)
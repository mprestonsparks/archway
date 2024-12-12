from setuptools import setup, find_packages

setup(
    name="archway",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    author="Archway Team",
    description="AI-driven development environment",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "archway=src.cli.main:main",
        ],
    },
)

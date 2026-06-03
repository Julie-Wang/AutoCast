from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autocast",
    version="0.1.0",
    author="Julie Wang",
    description="AI-powered content pipeline for open source projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Julie-Wang/AutoCast",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "edge-tts>=6.1.0",
        "markdown>=3.5.0",
        "jinja2>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "autocast=autocast.__main__:main",
        ],
    },
)

from setuptools import setup, find_packages

setup(
    name="kalshi-client",
    version="0.1.1",
    description="An unofficial python client for the Kalshi API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="vaguenebula",
    author_email="nebbylockedin@gmail.com",
    url="https://github.com/vaguenebula/kalshi-client",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "cryptography==44.0.0",
        "requests==2.32.3"
    ],
)

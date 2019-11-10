import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="binaryread",
    version="0.0.1",
    author="marfsama",
    author_email="marfsama@noreply.com",
    description="Helper functions and classes to read binary files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marfsama/binaryread",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pypegraph",
    version="0.1.1",
    author="Miguel Nicolás-Díaz",
    author_email="miguelcok27@gmail.com",
    description="A module for defining pipeline processing graphs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mnicolas94/pypegraph",
    packages=['pypegraph'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.6',
)
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymodulo",
    version="0.1.0",
    author="Dhruv Agarwal",
    author_email="dhruv.agarwal@alumni.ashoka.edu.in",
    description="Vehicle selection for drive-by sensing deployments to maximize coverage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/microsoft/Modulo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research"
    ],
    install_requires=[
    	"pandas>=1.0.3",
    	"pymongo>=3.10.1"
    ],
    python_requires='>=3.6',
)

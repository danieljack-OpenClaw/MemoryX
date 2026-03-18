from setuptools import setup, find_packages

setup(
    name="memoryx",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sentence-transformers",
        "chromadb",
        "tiktoken",
    ],
    python_requires=">=3.10",
)

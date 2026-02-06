from setuptools import setup, find_packages

setup(
    name="amnesia",
    version="1.0.0",
    description="Enterprise Machine Unlearning Platform",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "torch>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "pydantic>=2.0.0",
        "celery>=5.3.0",
        "redis>=4.6.0",
        "sqlalchemy>=2.0.0",
        "reportlab>=4.0.0",
        "loguru>=0.7.0",
    ],
    entry_points={
        "console_scripts": [
            "amnesia=api.main:run_server",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License 2.0",
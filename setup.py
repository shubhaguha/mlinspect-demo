from setuptools import setup, find_packages


setup(
    name="mlinspect-demo",
    version="1.0.0",
    description="Web app that demos the features of `mlinspect`",
    url="https://github.com/shubhaguha/mlinspect-demo",
    license="Apache License 2.0",
    python_requires="==3.8.*",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8"
    ],
    packages=find_packages(),
    package_data={
        "": ["assets"],
        "example_pipelines": ["healthcare", "adult"],
    },
    install_requires=[
        "dash<2",
        "dash-bootstrap-components<1",
        "dataclasses-serialization",
        "mlinspect[dev] @ git+https://github.com/stefan-grafberger/mlinspect.git@demo",
    ],
)

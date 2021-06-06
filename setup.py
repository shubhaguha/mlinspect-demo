from setuptools import setup, find_packages


setup(
    name="mlinspect-demo",
    version="1.0.0",
    description="Application to demo `mlinspect`",
    url="https://github.com/shubhaguha/mlinspect-demo",
    license="Apache License 2.0",
    python_requires="==3.8.*",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8"
    ],
    packages=find_packages(),
    install_requires=[
        "dash",
        "dash-bootstrap-components",

        # Insufficient because example_pipelines data are not available as package data
        # "mlinspect",
    ],
    # dependency_links=[
    #     "git+https://github.com/stefan-grafberger/mlinspect.git@demo",
    # ],
)
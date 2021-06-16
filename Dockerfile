# Use Python 3.8 for core libs e.g. ast
FROM python:3.8

# Update and install system dependencies for mlinspect
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y graphviz libgraphviz-dev

# Silence TensorFlow warnings
ENV TF_CPP_MIN_LOG_LEVEL="3"

# Install mlinspect-demo
COPY . /demo
WORKDIR /demo
RUN pip install -e .

# Run demo application
EXPOSE 8050
ENTRYPOINT [ "python", "-m", "mlinspect_demo" ]

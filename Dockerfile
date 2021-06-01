FROM python:3.8

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y graphviz libgraphviz-dev

ENV TF_CPP_MIN_LOG_LEVEL="3"

RUN git clone https://github.com/stefan-grafberger/mlinspect.git --branch demo
WORKDIR "/mlinspect"

COPY . /mlinspect

RUN pip install -e .[dev] dash dash-bootstrap-components

EXPOSE 8050
ENTRYPOINT [ "python", "app.py" ]

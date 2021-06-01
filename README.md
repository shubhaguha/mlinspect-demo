MLInspect Demo
===

MLInspect is a tool to inspect ML Pipelines in Python in the form of a DAG: <https://github.com/stefan-grafberger/mlinspect>

This repository is for running a demo server with a user interface for `mlinspect`.

Docker
---

Build locally and run:

	docker build . -t mlinspect-demo
	docker run -ti --rm --name mlinspect-demo -p 8050:8050 mlinspect-demo

Or pull the latest published Docker image and run:

	docker pull shubhaguha/mlinspect-demo
	docker run -ti --rm --name mlinspect-demo -p 8050:8050 shubhaguha/mlinspect-demo

Visit <http://localhost::8050> in your browser.

License
---

This library is licensed under the Apache 2.0 License.

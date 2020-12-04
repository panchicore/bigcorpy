# BigCorp API



[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

This is the challenge that must be completed in order to apply for a position in BigCorp

  - Make proxy-like API calls to the bigcorp API
  - Expand data dependencies

### Tech

This project uses a number of open source projects to work properly:

* Python3
* FastAPI - FastAPI framework, high performance, easy to learn, fast to code, ready for production
* Uvicorn - lightning-fast ASGI server implementation
* Swagger and Redoc - OpenAPI/Swagger-generated API Reference Documentation
* Pytest - For small test suites

### Installation

This project requires [Python3] to run.

Install the dependencies and start the server:

```sh
$ pip install -r requirements.txt
$ pytest
$ uvicorn main:app --reload
```


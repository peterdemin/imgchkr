Image Validator Take Home Test
Context

Labelbox’s Annotate product allows Machine Learning teams to efficiently send unstructured data of various data modalities (images, videos, audio, text, pdfs, DICOM studies, etc) to a human workforce to label.


The high-level goal of this project is to build a pipeline for validating image assets that Labelbox receives from its customers so each labeller is guaranteed a working asset to annotate.


Before you start …

During your implementation, feel free to leverage all/any open-source libraries that you deem fit. 


Although we currently use Python for most of our backend services with a sprinkling of Golang, feel free to use the language/technologies you are the most proficient in. 


You can assume that the evaluator of this project will be running a  *nix machine in a terminal with only make, vim, docker,  and docker-compose installed and won’t have any of the standard libraries and dependencies required for your implementation. 


Requirements


The service should accept an image, and return an HTTP 202 with the id of the asset after it has been successfully queued up for processing.
It accepts a reference to the image file and webhook URLs to notify the caller of progress.
For the sake of this exercise, you can assume the image is on the same machine as the server.

curl -H "content-type: application/json" -XPOST http://your-service/assets/image 

{
   # the location of the image
    “assetPath”: { 
        "location": "local",
        "path": "./images/foo"
    },

   # URLs to notify of pipeline progress
   “notifications”: {
     "onStart": "http://somevalidurl.com",
     "onSuccess": "http://somevalidurl.com",
     "onFailure": "http://somevalidurl.com"
   }
}

# When successful this returns
{
 "id": "abc12",
 "state": "queued"
}


After the asset has been accepted, it is queued up for validation. The validation rules are below. Your service should broadcast as many validation errors as possible to the user.


    The file is reachable by the server
    Only images are accepted
    Acceptable images are jpegs
    The jpeg does not have a width or height greater than 1000px.
    The notification URLs are valid


For the lifecycle of the pipeline, it broadcasts the state via the supplied notification URLs.

# called when the asset state moves from queued -> working
onStart({id: "assetId", state: "started"}) 

# called when working -> complete
onSuccess({id: "assetId", state: "success"})

# called when the state goes from anything to failed
onFailure({  
    "id": "assetId",
    "state": "failed",
    "errors": {
          "asset": ["is not a jpeg"]
          "onStart": ["is not a valid URL"],
          "onFailure": ["is not a valid URL"]
          }
 })


Developer Experience Requirements


The evaluator will run the following, which is expected to complete successfully.


make test-e2e # which will exercise your end to end system for scenarios
make test # runs unit tests on the various modules
make server # will run the service locally to allow the evaluator to access the service via curl commands



In addition to a working solution, please include a README.md file with at least the following topics addressed. If you can think of more topics to discuss feel free to add them! 


Getting Started


Running Tests


Architecture


Security Concerns


Scalability


How would you scale this implementation?


Monitoring


Thoughts on the key metrics you would track to understand the health of this service


Future work

Some ideas on how you would tackle any missing requirements

Ideas on how to make the service amenable to accepting more data types for validation

Anything else you can think of.






# Docker Flask Celery Redis

A basic [Docker Compose](https://docs.docker.com/compose/) template for orchestrating a [Flask](http://flask.pocoo.org/) application & a [Celery](http://www.celeryproject.org/) queue with [Redis](https://redis.io/)

### Installation

```bash
git clone https://github.com/mattkohl/docker-flask-celery-redis
```

### Build & Launch

```bash
docker-compose up -d --build
```

### Enable hot code reload

```
docker-compose -f docker-compose.yml -f docker-compose.development.yml up --build
```

This will expose the Flask application's endpoints on port `5001` as well as a [Flower](https://github.com/mher/flower) server for monitoring workers on port `5555`

To add more workers:
```bash
docker-compose up -d --scale worker=5 --no-recreate
```

To shut down:

```bash
docker-compose down
```


To change the endpoints, update the code in [api/app.py](api/app.py)

Task changes should happen in [celery-queue/tasks.py](celery-queue/tasks.py) 

---

adapted from [https://github.com/itsrifat/flask-celery-docker-scale](https://github.com/itsrifat/flask-celery-docker-scale)

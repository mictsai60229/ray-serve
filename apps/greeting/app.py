from starlette.requests import Request

from ray import serve
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from ray.serve.handle import DeploymentHandle

from apps.greeting.models import GreetingResponse, GreetingRequest

DEPLOYMENT_NAME = 'Greeting'

app = FastAPI()

@serve.deployment(
    name=DEPLOYMENT_NAME, # default as class name, should be unique
    max_ongoing_requests=5, 
    # num_replicas=2, 
    autoscaling_config= {
        "target_ongoing_requests": 2, # the requests waiting.
        "min_replicas": 1,
        "max_repliacs": 2,
    },
    ray_actor_options={
        # more in https://docs.ray.io/en/latest/ray-core/api/doc/ray.actor.ActorClass.options.html
        "num_cpus": 0.2, 
        "num_gpus": 0,
        # "memory": ,heap memory request in bytes
        # "label_selector": ["label_name", "value"], #might be helpful for gpu nodes or large models usage
    },
)
@serve.ingress(app)
class Greeting:

    def __init__(self, spanish_greeting: DeploymentHandle, french_greeting: DeploymentHandle):
        self.spanish_greeting = spanish_greeting
        self.french_greeting = french_greeting
    
    @app.get("/text")
    async def greeting(self, request: GreetingRequest):
        lang = request.lang
        if lang == 'fr':
            response = self.french_greeting.say_hello.remote()
        else:
            response = self.spanish_greeting.say_hello.remote()
        return GreetingResponse(
            text = await response
        )
    
    @app.get("/health")
    def get_health(self):
        return JSONResponse(content={"status": "ok"})
    
"""
deploy compostion of models,
Composition lets you break apart your application and independently scale each part
"""
@serve.deployment(
    autoscaling_config= {
        "target_ongoing_requests": 2, # the requests waiting.
        "min_replicas": 1,
        "max_repliacs": 2,
    },
)
class SpanishGreeting:
    def say_hello(self):
        return f"Hola"


@serve.deployment(
    autoscaling_config= {
        "target_ongoing_requests": 2, # the requests waiting.
        "min_replicas": 1,
        "max_repliacs": 3,
    },
)
class FrenchGreeting:
    def say_hello(self):
        return f"Bonjour"
    

spanish_greeting = SpanishGreeting.bind()
french_greeting = FrenchGreeting.bind()
greeting_app = Greeting.bind(spanish_greeting, french_greeting)
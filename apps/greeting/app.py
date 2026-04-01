from starlette.requests import Request

from ray import serve
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from apps.greeting.models import GreetingResponse

DEPLOYMENT_NAME = 'greeting'

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
    
    @app.get("/text")
    def translate_text(self): 
        return GreetingResponse()
    
    @app.get("/health")
    def get_health(self):
        return JSONResponse(content={"status": "ok"})
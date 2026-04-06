from fastapi import FastAPI
from ray import serve
from ray.serve.handle import DeploymentHandle, DeploymentResponse

from apps.chain.models import ChainRequest, ChainResponse

app = FastAPI()

@serve.deployment
class Adder:
    def __init__(self, increment: int):
        self._increment = increment

    def __call__(self, val: int) -> int:
        return val + self._increment


@serve.deployment
class Multiplier:
    def __init__(self, multiple: int):
        self._multiple = multiple

    def __call__(self, val: int) -> int:
        return val * self._multiple


@serve.deployment
@serve.ingress(app)
class Chain:
    def __init__(self, adder: DeploymentHandle, multiplier: DeploymentHandle):
        self._adder = adder
        self._multiplier = multiplier

    @app.get("/calculate")
    async def calculate(self, request: ChainRequest) -> ChainResponse:
        adder_response: DeploymentResponse = self._adder.remote(request.input)
        # Pass the adder response directly into the multiplier (no `await` needed).
        multiplier_response: DeploymentResponse = self._multiplier.remote(
            adder_response
        )
        # `await` the final chained response.
        value = await multiplier_response
        return ChainResponse(
            output = value
        )


chain_app = Chain.bind(
    Adder.bind(increment=1),
    Multiplier.bind(multiple=2),
)
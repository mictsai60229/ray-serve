from typing import AsyncGenerator, Generator

from ray import serve
from ray.serve.handle import DeploymentHandle, DeploymentResponseGenerator
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@serve.deployment
class Streamer:
    def __call__(self) -> Generator[int, None, None]:
        senetence = 'This is a streaming test!'
        for token in senetence.split():
            yield token


@serve.deployment
@serve.ingress(app)
class Stream:
    def __init__(self, streamer: DeploymentHandle):
        self._streamer = streamer.options(
            # Must set `stream=True` on the handle, then the output will be a
            # response generator.
            stream=True,
        )

    @app.get("/test")
    async def test(self) -> AsyncGenerator[int, None]:
        # Response generator can be used in an `async for` block.
        test_generator: DeploymentResponseGenerator = self._streamer.remote()
        # We must return a generator to FastAPI
        async def output_generator():
            async for chunk in test_generator:
                # Every yield here sends a chunk over the HTTP connection
                yield chunk
        
        return StreamingResponse(output_generator(), media_type="text/plain")


stream_app = Stream.bind(Streamer.bind())
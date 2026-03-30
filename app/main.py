import asyncio
from orchestrator.runtime import Runtime

runtime = Runtime()

asyncio.run(runtime.start())            
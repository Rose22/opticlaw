#!/bin/env python

import os
import sys
import asyncio
import core

async def main():
    # the manager class connects everything together
    manager = core.manager.Manager()
    # connect to openAI API
    manager.connect(core.config.get("model"), base_url=core.config.get("api_url"), api_key=core.config.get("api_key"))
    # run main loop
    await manager.run()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Shutting down..")
    exit()

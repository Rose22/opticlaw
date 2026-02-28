import os
import sys
import asyncio
import core

# load config from config.yaml
config = core.config.config

async def main():
    # initialize main manager class
    manager = core.manager.Manager()
    manager.connect(config.get("model"), base_url=config.get("api_url"), api_key=config.get("api_key"))

    # testing tool support
    import tool_test
    manager.add_tool_class(tool_test.Tools)

    # spawn all channel modules
    # spawned_channels = []

    # for channel in channels.get_all():
        #spawned_channels.append(channel.run(client, broadcaster))
        # spawned_channels.append(channel.run(client))
        # core.log("init", f"Channel {channel.__name__} started")

    # run all channels simultaneously
    # await asyncio.gather(*spawned_channels)

    await manager.run()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Shutting down..")
    exit()

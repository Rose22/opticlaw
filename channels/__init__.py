import asyncio

def get_all():
    # temporary fix for now
    import channels.chan_cli
    import channels.chan_discord
    #return (channels.chan_cli.ChannelCli,)
    return (channels.chan_cli.ChannelCli, channels.chan_discord.ChannelDiscord)

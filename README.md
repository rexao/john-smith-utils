# John Smith Utils

This is a collection of miscellaneous utils. No concrete development plans.

## Emote Sync Utils

### Summary

`array_sync.py` `guild_sync.py`

The scripts download emotes from BetterTTV, FrankerFaceZ and 7TV and sync to Discord servers.

**Array Sync** syncs to an array of servers such that with Nitro privileges in mind you can use the Twitch emotes everywhere.

**Guild Sync** syncs to a specific server and makes them (the static ones 😟) available for everyone.

### Setup

#### 1. Set up the server array

For Array Sync, it's required to setup an array of server first. 

Create as many servers as it's needed to accommodate the emotes (like ~10 of them). 

It's recommended to put them into a folder and place the folder on top so that the emotes in the array show up as the default (as opposed to e.g. `:Pog~1:`).

#### 2. Configure `config.json`

`"twitch_uid"` : Twitch user ID. Tools that convert Twitch usernames into UID are available online.

`"stv_uid"` : 7TV user ID. The ID can be found in the URL of an 7TV user page.

`"js_token"` : Discord bot token.

`"labo_array"` : Key in the server IDs. (Only required for Array Sync)
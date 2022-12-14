
# John Smith Utils

This is a collection of miscellaneous utils. No concrete development plans.

## Emote Sync Utils

### Summary

`array_sync.py` `guild_sync.py`

The scripts download emotes from BetterTTV, FrankerFaceZ and 7TV and sync to Discord servers.

**Array Sync** syncs to an array of servers such that with Nitro privileges in mind you can use the Twitch emotes everywhere.

**Guild Sync** syncs to a specific server and makes them (the non-animated ones 😟) available for everyone.

### Setup

#### 1. Set up the server array

For **Array Sync**, it's required to setup an array of server on Discord first. 

Create as many servers as needed to accommodate the emotes (~10 of them). 

Tips: put the array servers into a folder and place the folder on the topmost so that the emotes in the array show up as the default (as opposed to e.g. `:Pog~1:`).

#### 2. Configure `config.json`

| Key | Data Type | Value |
|--|--|--|
| `"twitch_uid"` | number | Twitch user ID. Tools that convert Twitch usernames into UID are available online. |
| `"stv_uid"` | string | 7TV user ID. The ID can be found in the URL of an 7TV user page. |
| `"js_token"` | string | Discord bot token. |
| `"labo_array"` | number (`id`) | Key in the server IDs. (For Array Sync) |
| `"target_guilds"` | number (`id`, `emote_limit`) | Key in the server IDs and the respective emoji limit (default 50) for each category. (For Guild Sync) |

#### 3. For macOS: `ulimit -Sn`

On macOS (confirmed on Big Sur 11.7), the limit on the number of file descriptors a process may have defaults to 256 and causes the scripts to raise `OSError: [Errno 24] Too many open files` in my testing. They run for me at 2000 but feel free to set it to whatever that fits your case.

Run this command before running the script: `ulimit -Sn 2000`

See also: https://www.ibm.com/docs/en/aix/7.2?topic=u-ulimit-command
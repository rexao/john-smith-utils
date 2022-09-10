import asyncio
import json
import os
import shutil
import time

from main import BetterTTV, Discord, FrankerFaceZ, now


async def main():
    target_guild_id = [input('Enter guild ID: ')]
    target_guild_emoji_limit = int(input('Enter guild emoji limit: '))

    with open('config.json', 'r') as cfg:
        config = json.load(cfg)
    twitch_uid = config['twitch_uid']
    js_token = config['js_token']

    print('\033[90m'+u'\u2500'*32+'\033[0m')
    print(f"{now()} Downloading BetterTTV channel emotes...")
    bttv_channel = BetterTTV(twitch_uid=twitch_uid)
    bttv_channel.dir = f'emotes_guild/BetterTTV/{twitch_uid}'
    if os.path.exists(bttv_channel.dir):
        shutil.rmtree(bttv_channel.dir)
    os.makedirs(bttv_channel.dir)
    bttv_channel_emotes = await bttv_channel.get_json()
    bttv_channel_downloads = [bttv_channel.download_emote(emote) for emote in bttv_channel_emotes]
    await asyncio.gather(*bttv_channel_downloads)

    print('\033[90m'+u'\u2500'*32+'\033[0m')
    print(f"{now()} Downloading FrankerFaceZ channel emotes...")
    ffz_channel = FrankerFaceZ(twitch_uid=twitch_uid)
    ffz_channel.dir = f'emotes_guild/FrankerFaceZ/{twitch_uid}'
    if os.path.exists(ffz_channel.dir):
        shutil.rmtree(ffz_channel.dir)
    os.makedirs(ffz_channel.dir)
    ffz_channel_emotes = await ffz_channel.get_json()
    ffz_channel_downloads = [ffz_channel.download_emote(emote) for emote in ffz_channel_emotes]
    await asyncio.gather(*ffz_channel_downloads)

    print('\033[90m'+u'\u2500'*32+'\033[0m')
    print(f"{now()} Trimming emote library...")
    bttv_channel_trimming = [bttv_channel.keep_largest_qualified(emote=emote) for emote in bttv_channel_emotes]
    await asyncio.gather(*bttv_channel_trimming)
    
    emote_syncs, animated_emote_syncs = [], []
    for emote in ffz_channel_emotes:
        search = [
            f"{ffz_channel.dir}/{file}" for file in os.listdir(ffz_channel.dir)
            if file.startswith(f"{emote['code']}_{emote['id']}")
        ]
        if not search:
            continue
        emote_syncs.append({
            "name": emote['code'],
            "image_path": search[-1]
        })
    for emote in bttv_channel_emotes:
        search = [
            f"{bttv_channel.dir}/{file}" for file in os.listdir(bttv_channel.dir)
            if file.startswith(f"{emote['code']}_{emote['id']}")
        ]
        if not search:
            continue
        content = {
            "name": emote['code'],
            "image_path": search[-1]
        }
        if emote['imageType'] == 'png':
            emote_syncs.append(content)
        elif emote['imageType'] == 'gif':
            animated_emote_syncs.append(content)
        
    discord = Discord(js_token=js_token, labo_array=target_guild_id)
    for idx, guild in enumerate(discord.array):
        start, end = idx*target_guild_emoji_limit, idx*target_guild_emoji_limit+target_guild_emoji_limit
        guild_emojis = await discord.get_gulid_emojis(guild_id=guild)
        before_list = [emoji for emoji in guild_emojis if not emoji['animated']]
        animated_before_list = [emoji for emoji in guild_emojis if emoji['animated']]
        after_list = emote_syncs[start:end]
        animated_after_list = animated_emote_syncs[start:end]
        # print('guild_emojis', guild, guild_emojis)
        # print('before_list', guild, before_list)
        # print('animated_before_list', guild, animated_before_list)
        # print('after_list', guild, after_list)
        # print('animated_after_list', guild, animated_after_list)

        delete_list = [
            emoji for emoji in before_list
            if emoji['name'] not in [emote['name'] for emote in after_list]
        ]
        animated_delete_list = [
            emoji for emoji in animated_before_list
            if emoji['name'] not in [emote['name'] for emote in animated_after_list]
        ]
        upload_list = [
            emote for emote in after_list
            if emote['name'] not in [emoji['name'] for emoji in before_list]
        ]
        animated_upload_list = [
            emote for emote in animated_after_list
            if emote['name'] not in [emoji['name'] for emoji in animated_before_list]
        ]

        print('\033[90m'+u'\u2500'*32+'\033[0m')
        print(f"""{now()} Processing guild {guild} - deleting: {
            [emoji['name'] for emoji in delete_list] + [emoji['name'] for emoji in animated_delete_list]
        }""")
        await asyncio.gather(*[
            discord.delete_emote(guild_id=guild, emoji_name=emoji['name'], emoji_id=emoji['id'])
            for emoji in delete_list
        ])
        await asyncio.gather(*[
            discord.delete_emote(guild_id=guild, emoji_name=emoji['name'], emoji_id=emoji['id'])
            for emoji in animated_delete_list
        ])
        
        print(f"""{now()} Processing guild {guild} - posting: {
            [emote['name'] for emote in upload_list] + [emote['name'] for emote in animated_upload_list]
        }""")
        await asyncio.gather(*[
            discord.upload_emote(guild_id=guild, emote_name=emote['name'], emote_image_path=emote['image_path'])
            for emote in upload_list
        ])
        await asyncio.gather(*[
            discord.upload_emote(guild_id=guild, emote_name=emote['name'], emote_image_path=emote['image_path'])
            for emote in animated_upload_list
        ])

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    print('\033[90m'+u'\u2500'*32+'\033[0m')
    print(f"Elapsed time: {time.time()-start_time}s")
    print('\033[90m'+u'\u2500'*32+'\033[0m')

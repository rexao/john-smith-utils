import asyncio
import json
import os
import time

from main import BetterTTV, Discord, FrankerFaceZ, SevenTV, now


async def main():
    with open('config.json', 'r') as cfg:
        config = json.load(cfg)
    twitch_uid = config['twitch_uid']
    stv_uid = config['stv_uid']
    js_token = config['js_token']
    labo_array = [guild['id'] for guild in config['labo_array']]

    print('\033[90m'+u'\u2500'*32+'\033[0m')
    print(f"{now()} Downloading BetterTTV global emotes...")
    bttv_global = BetterTTV()
    bttv_global_emotes = await bttv_global.get_json()
    bttv_global_downloads = [bttv_global.download_emote(emote) for emote in bttv_global_emotes]
    await asyncio.gather(*bttv_global_downloads)
    
    print('\033[90m'+u'\u2500'*32+'\033[0m')
    print(f"{now()} Downloading 7TV global emotes...")
    stv_global = SevenTV()
    stv_global_emotes = await stv_global.get_json()
    stv_global_downloads = [stv_global.download_emote(emote) for emote in stv_global_emotes]
    await asyncio.gather(*stv_global_downloads)
    
    print('\033[90m'+u'\u2500'*32+'\033[0m')
    print(f"{now()} Downloading FrankerFaceZ channel emotes...")
    ffz_channel = FrankerFaceZ(twitch_uid=twitch_uid)
    ffz_channel_emotes = await ffz_channel.get_json()
    ffz_channel_downloads = [ffz_channel.download_emote(emote) for emote in ffz_channel_emotes]
    await asyncio.gather(*ffz_channel_downloads)
    
    print('\033[90m'+u'\u2500'*32+'\033[0m')
    print(f"{now()} Downloading BetterTTV channel emotes...")
    bttv_channel = BetterTTV(twitch_uid=twitch_uid)
    bttv_channel_emotes = await bttv_channel.get_json()
    bttv_channel_downloads = [bttv_channel.download_emote(emote) for emote in bttv_channel_emotes]
    await asyncio.gather(*bttv_channel_downloads)
    
    print('\033[90m'+u'\u2500'*32+'\033[0m')
    print(f"{now()} Downloading 7TV channel emotes...")
    stv_channel = SevenTV(stv_uid=stv_uid)
    stv_channel_emotes = await stv_channel.get_json()
    downloads = [stv_channel.download_emote(emote=emote) for emote in stv_channel_emotes]
    await asyncio.gather(*downloads)
    
    print('\033[90m'+u'\u2500'*32+'\033[0m')
    print(f"{now()} Converting 7TV emotes...")
    stv_global_converts = [
        stv_global.webp_to_gif(emote_path=f'{stv_global.dir}/{emote}')
        for emote in os.listdir(stv_global.dir)
        if stv_global.check_animated(f'{stv_global.dir}/{emote}')
    ]
    await asyncio.gather(*stv_global_converts)
    stv_channel_converts = [
        stv_channel.webp_to_gif(emote_path=f'{stv_channel.dir}/{emote}') 
        for emote in os.listdir(stv_channel.dir) 
        if stv_channel.check_animated(f'{stv_channel.dir}/{emote}')
    ]
    await asyncio.gather(*stv_channel_converts)
    
    print('\033[90m'+u'\u2500'*32+'\033[0m')
    print(f"{now()} Trimming emote library...")
    bttv_global_trimming = [bttv_global.keep_largest_qualified(emote=emote) for emote in bttv_global_emotes]
    await asyncio.gather(*bttv_global_trimming)
    stv_global_trimming = [stv_global.keep_largest_qualified(emote) for emote in stv_global_emotes]
    await asyncio.gather(*stv_global_trimming)
    bttv_channel_trimming = [bttv_channel.keep_largest_qualified(emote=emote) for emote in bttv_channel_emotes]
    await asyncio.gather(*bttv_channel_trimming)
    stv_channel_trimming = [stv_channel.keep_largest_qualified(emote) for emote in stv_channel_emotes]
    await asyncio.gather(*stv_channel_trimming)

    emote_syncs, animated_emote_syncs = [], []
    for emote in bttv_global_emotes:
        search = [
            f"{bttv_global.dir}/{file}" for file in os.listdir(bttv_global.dir)
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
    for emote in stv_global_emotes:
        search = [
            f"{stv_global.dir}/{file}" for file in os.listdir(stv_global.dir)
            if file.startswith(f"{emote['name']}_{emote['id']}")
        ]
        if not search:
            continue
        content = {
            "name": emote['name'],
            "image_path": search[-1]
        }
        if search[-1].endswith('.webp'):
            emote_syncs.append(content)
        elif search[-1].endswith('.gif'):
            animated_emote_syncs.append(content)
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
    for emote in stv_channel_emotes:
        search = [
            f"{stv_channel.dir}/{file}" for file in os.listdir(stv_channel.dir)
            if file.startswith(f"{emote['name']}_{emote['id']}")
        ]
        if not search:
            continue
        content = {
            "name": emote['name'],
            "image_path": search[-1]
        }
        if search[-1].endswith('.webp'):
            emote_syncs.append(content)
        elif search[-1].endswith('.gif'):
            animated_emote_syncs.append(content)
    # print('emote_syncs', emote_syncs)
    # print('animated_emote_syncs', animated_emote_syncs)
    
    discord = Discord(js_token=js_token, labo_array=labo_array)
    for idx, guild in enumerate(discord.array):
        start, end = idx*50, idx*50+50
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
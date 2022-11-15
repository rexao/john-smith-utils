import asyncio
import json
import os
import time
from typing import List

from main import (
    DiscordEmote, DiscordGuild,
    BetterTTV, FrankFaceZ, SevenTV,
    ThirdPartyEmote, BetterTTVEmote, FrankerFaceZEmote, SevenTVEmote,
    divider, timestamp
)



async def main():

    # Read config.json
    with open('config.json', 'r') as cfg:
        config = json.load(cfg)
    twitch_uid = config['twitch_uid']
    stv_uid = config['stv_uid']
    js_token = config['js_token']
    labo_array = [DiscordGuild(
        js_token=js_token, id=guild['id'], emoji_limit=50
    ) for guild in config['labo_array']]
    
    # Initialize objects
    bttv_global = BetterTTV(base_dir='array-sync-emotes')
    stv_global = SevenTV(base_dir='array-sync-emotes')
    ffz_channel = FrankFaceZ(base_dir='array-sync-emotes', twitch_uid=twitch_uid)
    bttv_channel = BetterTTV(base_dir='array-sync-emotes', twitch_uid=twitch_uid)
    stv_channel = SevenTV(base_dir='array-sync-emotes', stv_uid=stv_uid)

    # Download BetterTTV global emotes
    print(divider)
    print(f"{timestamp()} Downloading BetterTTV global emotes...")
    bttv_global_json = await bttv_global.get_json()
    bttv_global_emotes: List[BetterTTVEmote] = []
    for json_dict in bttv_global_json:
        bttv_global_emotes.append(await BetterTTVEmote().read_from_json(json=json_dict))
    bttv_global_downloads = [emote.download_emote(dir=bttv_global.dir) for emote in bttv_global_emotes]
    await asyncio.gather(*bttv_global_downloads)

    # Download 7TV global emotes
    print(divider)
    print(f"{timestamp()} Downloading 7TV global emotes...")
    stv_global_json = await stv_global.get_json()
    stv_global_emotes: List[SevenTVEmote] = []
    for json_dict in stv_global_json:
        stv_global_emotes.append(await SevenTVEmote().read_from_json(json=json_dict))
    stv_global_downloads = [emote.download_emote(dir=stv_global.dir) for emote in stv_global_emotes]
    await asyncio.gather(*stv_global_downloads)

    # Download FrankerFaceZ channel emotes
    print(divider)
    print(f"{timestamp()} Downloading FrankerFaceZ channel emotes...")
    ffz_channel_json = await ffz_channel.get_json()
    ffz_channel_emotes: List[FrankerFaceZEmote] = []
    for json_dict in ffz_channel_json:
        ffz_channel_emotes.append(await FrankerFaceZEmote().read_from_json(json=json_dict))
    ffz_channel_downloads = [emote.download_emote(dir=ffz_channel.dir) for emote in ffz_channel_emotes]
    await asyncio.gather(*ffz_channel_downloads)
    
    # Download BetterTTV channel emotes
    print(divider)
    print(f"{timestamp()} Downloading BetterTTV channel emotes...")
    bttv_channel_json = await bttv_channel.get_json()
    bttv_channel_emotes: List[BetterTTVEmote] = []
    for json_dict in bttv_channel_json:
        bttv_channel_emotes.append(await BetterTTVEmote().read_from_json(json=json_dict))
    bttv_channel_downloads = [emote.download_emote(dir=bttv_channel.dir) for emote in bttv_channel_emotes]
    await asyncio.gather(*bttv_channel_downloads)

    # Download 7TV channel emotes
    print(divider)
    print(f"{timestamp()} Downloading 7TV channel emotes...")
    stv_channel_json = await stv_channel.get_json()
    stv_channel_emotes: List[SevenTVEmote] = []
    for json_dict in stv_channel_json:
        stv_channel_emotes.append(await SevenTVEmote().read_from_json(json=json_dict))
    stv_channel_downloads = [emote.download_emote(dir=stv_channel.dir) for emote in stv_channel_emotes]
    await asyncio.gather(*stv_channel_downloads)

    # Remove oversized emotes / Generate emote file lists
    print(divider)
    print(f"{timestamp()} Trimming emote library...")
    bttv_global_emote_files: List[ThirdPartyEmote] = []
    for emote in os.listdir(bttv_global.dir):
        emote_path = f"{bttv_global.dir}/{emote}"
        emote = ThirdPartyEmote().read_from_path(emote_path)
        bttv_global_emote_files.append(emote)
    bttv_global_emote_ids = set([emote.id for emote in bttv_global_emote_files])
    for id in bttv_global_emote_ids:
        emote_variants = [emote for emote in bttv_global_emote_files if emote.id==id]
        qualified_size = [
            variant.file_size for variant in emote_variants
            if variant.file_size<=262144
        ]
        qualified_size = max(qualified_size) if qualified_size else None
        for variant in emote_variants:
            if variant.file_size!=qualified_size:
                variant.delete()
    bttv_global_emote_files: List[ThirdPartyEmote] = []
    for emote in os.listdir(bttv_global.dir):
        emote_path = f"{bttv_global.dir}/{emote}"
        emote = ThirdPartyEmote().read_from_path(emote_path)
        bttv_global_emote_files.append(emote)
    
    stv_global_emote_files: List[ThirdPartyEmote] = []
    for emote in os.listdir(stv_global.dir):
        emote_path = f"{stv_global.dir}/{emote}"
        emote = ThirdPartyEmote().read_from_path(emote_path)
        if emote_path.endswith('.webp') and emote.check_animated():
            emote = emote.convert_webp_to_gif()
        stv_global_emote_files.append(emote)
    stv_global_emote_ids = set([emote.id for emote in stv_global_emote_files])
    for id in stv_global_emote_ids:
        emote_variants = [emote for emote in stv_global_emote_files if emote.id==id]
        qualified_size = [
            variant.file_size for variant in emote_variants
            if variant.file_size<=262144
        ]
        qualified_size = max(qualified_size) if qualified_size else None
        for variant in emote_variants:
            if variant.file_size!=qualified_size:
                variant.delete()
    stv_global_emote_files: List[ThirdPartyEmote] = []
    for emote in os.listdir(stv_global.dir):
        emote_path = f"{stv_global.dir}/{emote}"
        emote = ThirdPartyEmote().read_from_path(emote_path)
        stv_global_emote_files.append(emote)
    
    ffz_channel_emote_files: List[ThirdPartyEmote] = []
    for emote in os.listdir(ffz_channel.dir):
        emote_path = f"{ffz_channel.dir}/{emote}"
        emote = ThirdPartyEmote().read_from_path(emote_path)
        ffz_channel_emote_files.append(emote)
    ffz_channel_emote_ids = set([emote.id for emote in ffz_channel_emote_files])
    for id in ffz_channel_emote_ids:
        emote_variants = [emote for emote in ffz_channel_emote_files if emote.id==id]
        qualified_size = [
            variant.file_size for variant in emote_variants
            if variant.file_size<=262144
        ]
        qualified_size = max(qualified_size) if qualified_size else None
        for variant in emote_variants:
            if variant.file_size!=qualified_size:
                variant.delete()
    ffz_channel_emote_files: List[ThirdPartyEmote] = []
    for emote in os.listdir(ffz_channel.dir):
        emote_path = f"{ffz_channel.dir}/{emote}"
        emote = ThirdPartyEmote().read_from_path(emote_path)
        ffz_channel_emote_files.append(emote)
    
    bttv_channel_emote_files: List[ThirdPartyEmote] = []
    for emote in os.listdir(bttv_channel.dir):
        emote_path = f"{bttv_channel.dir}/{emote}"
        emote = ThirdPartyEmote().read_from_path(emote_path)
        bttv_channel_emote_files.append(emote)
    bttv_channel_emote_ids = set([emote.id for emote in bttv_channel_emote_files])
    for id in bttv_channel_emote_ids:
        emote_variants = [emote for emote in bttv_channel_emote_files if emote.id==id]
        qualified_size = [
            variant.file_size for variant in emote_variants
            if variant.file_size<=262144
        ]
        qualified_size = max(qualified_size) if qualified_size else None
        for variant in emote_variants:
            if variant.file_size!=qualified_size:
                variant.delete()
    bttv_channel_emote_files: List[ThirdPartyEmote] = []
    for emote in os.listdir(bttv_channel.dir):
        emote_path = f"{bttv_channel.dir}/{emote}"
        emote = ThirdPartyEmote().read_from_path(emote_path)
        bttv_channel_emote_files.append(emote)
    
    stv_channel_emote_files: List[ThirdPartyEmote] = []
    for emote in os.listdir(stv_channel.dir):
        emote_path = f"{stv_channel.dir}/{emote}"
        emote = ThirdPartyEmote().read_from_path(emote_path)
        if emote_path.endswith('.webp') and emote.check_animated():
            emote = emote.convert_webp_to_gif()
        stv_channel_emote_files.append(emote)
    stv_channel_emote_ids = set([emote.id for emote in stv_channel_emote_files])
    for id in stv_channel_emote_ids:
        emote_variants = [emote for emote in stv_channel_emote_files if emote.id==id]
        qualified_size = [
            variant.file_size for variant in emote_variants
            if variant.file_size<=262144
        ]
        qualified_size = max(qualified_size) if qualified_size else None
        for variant in emote_variants:
            if variant.file_size!=qualified_size:
                variant.delete()
    stv_channel_emote_files: List[ThirdPartyEmote] = []
    for emote in os.listdir(stv_channel.dir):
        emote_path = f"{stv_channel.dir}/{emote}"
        emote = ThirdPartyEmote().read_from_path(emote_path)
        stv_channel_emote_files.append(emote)
    
    # Generate lists of new emotes to be sync (separated by static/animated)
    new_static_emotes: List[ThirdPartyEmote] = []
    new_animated_emotes: List[ThirdPartyEmote] = []
    for emote in bttv_global_emotes:
        emote_file = [emote_file for emote_file in bttv_global_emote_files if emote_file.id==str(emote.id)]
        if not emote_file:
            continue
        elif len(emote_file)>1:
            raise ValueError('Trimming unclean!!')
        if emote_file[0].animated:
            new_animated_emotes += emote_file
        else:
            new_static_emotes += emote_file
    for emote in stv_global_emotes:
        emote_file = [emote_file for emote_file in stv_global_emote_files if emote_file.id==str(emote.id)]
        if not emote_file:
            continue
        elif len(emote_file)>1:
            raise ValueError('Trimming unclean!!')
        if emote_file[0].check_animated():
            new_animated_emotes += emote_file
        else:
            new_static_emotes += emote_file
    for emote in ffz_channel_emotes:
        emote_file = [emote_file for emote_file in ffz_channel_emote_files if emote_file.id==str(emote.id)]
        if not emote_file:
            continue
        elif len(emote_file)>1:
            raise ValueError('Trimming unclean!!')
        if emote_file[0].animated:
            new_animated_emotes += emote_file
        else:
            new_static_emotes += emote_file
    for emote in bttv_channel_emotes:
        emote_file = [emote_file for emote_file in bttv_channel_emote_files if emote_file.id==str(emote.id)]
        if not emote_file:
            continue
        elif len(emote_file)>1:
            raise ValueError('Trimming unclean!!')
        if emote_file[0].animated:
            new_animated_emotes += emote_file
        else:
            new_static_emotes += emote_file
    for emote in stv_channel_emotes:
        emote_file = [emote_file for emote_file in stv_channel_emote_files if emote_file.id==str(emote.id)]
        if not emote_file:
            continue
        elif len(emote_file)>1:
            raise ValueError('Trimming unclean!!')
        if emote_file[0].check_animated():
            new_animated_emotes += emote_file
        else:
            new_static_emotes += emote_file
    
    # Generate list of archived emotes
    old_emotes: List[ThirdPartyEmote] = []
    if os.path.exists(bttv_global.archive_dir):
        for emote in os.listdir(bttv_global.archive_dir):
            emote_path = f"{bttv_global.archive_dir}/{emote}"
            old_emotes.append(
                ThirdPartyEmote().read_from_path(emote_path)
            )
    if os.path.exists(stv_global.archive_dir):
        for emote in os.listdir(stv_global.archive_dir):
            emote_path = f"{stv_global.archive_dir}/{emote}"
            old_emotes.append(
                ThirdPartyEmote().read_from_path(emote_path)
            )
    if os.path.exists(ffz_channel.archive_dir):
        for emote in os.listdir(ffz_channel.archive_dir):
            emote_path = f"{ffz_channel.archive_dir}/{emote}"
            old_emotes.append(
                ThirdPartyEmote().read_from_path(emote_path)
            )
    if os.path.exists(bttv_channel.archive_dir):
        for emote in os.listdir(bttv_channel.archive_dir):
            emote_path = f"{bttv_channel.archive_dir}/{emote}"
            old_emotes.append(
                ThirdPartyEmote().read_from_path(emote_path)
            )
    if os.path.exists(stv_channel.archive_dir):
        for emote in os.listdir(stv_channel.archive_dir):
            emote_path = f"{stv_channel.archive_dir}/{emote}"
            old_emotes.append(
                ThirdPartyEmote().read_from_path(emote_path)
            )

    # Generate list of modified emotes to be synced
    emote_modifies: List[ThirdPartyEmote] = []
    for emote in new_static_emotes+new_animated_emotes:
        if (
            emote.code in [old_emote.code for old_emote in old_emotes] and
            emote.id not in [old_emote.id for old_emote in old_emotes if old_emote.code==emote.code]
        ):
            emote_modifies.append(emote)


    for idx, guild in enumerate(labo_array):
        # Read Discord guild emotes / Generate list of emotes this guild will have
        print(divider)
        print(f"{timestamp()} Processing array guild {guild.id}...")
        guild_emojis_json = await guild.get_gulid_emojis()
        guild_emotes = [DiscordEmote().read_from_json(json=json_dict) for json_dict in guild_emojis_json]
        new_emotes = new_static_emotes[idx*50:idx*50+50]+new_animated_emotes[idx*50:idx*50+50]
        
        # 1. Replace modified emotes
        modify_deletes = [
            guild.delete_emote(id=emote.id, name=emote.name)
            for emote in guild_emotes
            if emote.name in [emote.code for emote in emote_modifies]
        ]
        await asyncio.gather(*modify_deletes)
        modify_uploads = [
            guild.upload_emote(name=emote.code, image=await emote.get_uri())
            for emote in emote_modifies
        ]
        await asyncio.gather(*modify_uploads)

        # 2. Delete obsolete emotes
        emote_deletes: List[DiscordEmote] = [
            emote for emote in guild_emotes
            if emote.name not in [emote.code for emote in new_emotes]
        ]
        deletes = [
            guild.delete_emote(id=emote.id, name=emote.name) 
            for emote in emote_deletes
        ]
        await asyncio.gather(*deletes)

        # 3. Posts new emotes
        emote_posts: List[ThirdPartyEmote] = [
            emote for emote in new_emotes
            if emote.code not in [emote.name for emote in guild_emotes]
        ]
        posts = [
            guild.upload_emote(name=emote.code, image=await emote.get_uri())
            for emote in emote_posts
        ]
        await asyncio.gather(*posts)



if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    print(divider)
    print(f"Elapsed time: {time.time()-start_time}s")
    print(divider)
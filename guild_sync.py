import asyncio
import json
import os
import time
from typing import List

from main import (
    DiscordEmote, DiscordGuild,
    BetterTTV, FrankFaceZ,
    ThirdPartyEmote, BetterTTVEmote, FrankerFaceZEmote,
    divider, timestamp
)



async def main():
    
    # Read config.json
    with open('config.json', 'r') as cfg:
        config = json.load(cfg)
    twitch_uid = config['twitch_uid']
    js_token = config['js_token']
    target_guilds = [DiscordGuild(
        js_token=js_token, id=guild['id'], emoji_limit=guild['emoji_limit']
    ) for guild in config['target_guilds']]
    
    # Initialize objects
    bttv_channel = BetterTTV(base_dir='guild-sync-emotes', twitch_uid=twitch_uid)
    ffz = FrankFaceZ(base_dir='guild-sync-emotes', twitch_uid=twitch_uid)

    # Download BetterTTV channel emotes
    print(divider)
    print(f"{timestamp()} Downloading BetterTTV channel emotes...")
    bttv_channel_json = await bttv_channel.get_json()
    bttv_channel_emotes: List[BetterTTVEmote] = []
    for json_dict in bttv_channel_json:
        bttv_channel_emotes.append(await BetterTTVEmote().read_from_json(json=json_dict))
    bttv_channel_downloads = [emote.download_emote(dir=bttv_channel.dir) for emote in bttv_channel_emotes]
    await asyncio.gather(*bttv_channel_downloads)

    # Download FrankerFaceZ channel emotes
    print(divider)
    print(f"{timestamp()} Downloading FrankerFaceZ channel emotes...")
    ffz_json = await ffz.get_json()
    ffz_emotes: List[FrankerFaceZEmote] = []
    for json_dict in ffz_json:
        ffz_emotes.append(await FrankerFaceZEmote().read_from_json(json=json_dict))
    ffz_downloads = [emote.download_emote(dir=ffz.dir) for emote in ffz_emotes]
    await asyncio.gather(*ffz_downloads)

    # Remove oversized emotes / Generate emote file lists
    print(divider)
    print(f"{timestamp()} Trimming emote library...")
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
    
    ffz_emote_files: List[ThirdPartyEmote] = []
    for emote in os.listdir(ffz.dir):
        emote_path = f"{ffz.dir}/{emote}"
        emote = ThirdPartyEmote().read_from_path(emote_path)
        ffz_emote_files.append(emote)
    ffz_emote_ids = set([emote.id for emote in ffz_emote_files])
    for id in ffz_emote_ids:
        emote_variants = [emote for emote in ffz_emote_files if emote.id==id]
        qualified_size = [
            variant.file_size for variant in emote_variants
            if variant.file_size<=262144
        ]
        qualified_size = max(qualified_size) if qualified_size else None
        for variant in emote_variants:
            if variant.file_size!=qualified_size:
                variant.delete()
    ffz_emote_files: List[ThirdPartyEmote] = []
    for emote in os.listdir(ffz.dir):
        emote_path = f"{ffz.dir}/{emote}"
        emote = ThirdPartyEmote().read_from_path(emote_path)
        ffz_emote_files.append(emote)

    # Generate lists of new emotes to be sync (separated by static/animated)
    new_static_emotes: List[ThirdPartyEmote] = []
    new_animated_emotes: List[ThirdPartyEmote] = []
    for emote in ffz_emotes:
        emote_file = [emote_file for emote_file in ffz_emote_files if emote_file.id==str(emote.id)]
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
    
    # Generate list of archived emotes
    old_emotes: List[ThirdPartyEmote] = []
    if os.path.exists(ffz.archive_dir):
        for emote in os.listdir(ffz.archive_dir):
            emote_path = f"{ffz.archive_dir}/{emote}"
            old_emotes.append(
                ThirdPartyEmote().read_from_path(emote_path)
            )
    if os.path.exists(bttv_channel.archive_dir):
        for emote in os.listdir(bttv_channel.archive_dir):
            emote_path = f"{bttv_channel.archive_dir}/{emote}"
            old_emotes.append(
                ThirdPartyEmote().read_from_path(emote_path)
            )

    
    

    for guild in target_guilds:
        # Read Discord guild emotes / Generate list of emotes this guild will have
        print(divider)
        print(f"{timestamp()} Processing guild {guild.id} (max {guild.emoji_limit}+{guild.emoji_limit} emotes)...")
        guild_emojis_json = await guild.get_gulid_emojis()
        guild_emotes = [DiscordEmote().read_from_json(json=json_dict) for json_dict in guild_emojis_json]
        new_emotes = new_static_emotes[:guild.emoji_limit]+new_animated_emotes[:guild.emoji_limit]
        
        # Generate list of modified emotes to be synced
        emote_modifies: List[ThirdPartyEmote] = []
        for emote in new_emotes:
            if (
                emote.code in [old_emote.code for old_emote in old_emotes] and
                emote.id not in [old_emote.id for old_emote in old_emotes if old_emote.code==emote.code]
            ):
                emote_modifies.append(emote)

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
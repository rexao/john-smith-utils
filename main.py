import asyncio
import base64
import datetime
import json
import os
import shutil
from typing import Union

import aiofiles
import aiohttp
from PIL import Image, ImageSequence

today = datetime.date.today().strftime('%Y-%m-%d')

def now():
    return f"\033[90m{datetime.datetime.now().strftime('%H:%M:%S')}\033[0m"

def emote_code_legalization(emote_code: str):
    replacements = {
        ":": "colon",
        "&": "and",
        "+": "plus",
        "-": "minus",
    }
    for replacement in replacements:
        emote_code = emote_code.replace(replacement, replacements[replacement])[:32]
    return emote_code


class BetterTTV():
    def __init__(self, twitch_uid: Union[int, str] = None) -> None:
        self.api = f'https://api.betterttv.net/3/cached/users/twitch/{twitch_uid}' if twitch_uid else 'https://api.betterttv.net/3/cached/emotes/global'
        self.cdn = 'https://cdn.betterttv.net/emote'
        self.dir = f'emotes/BetterTTV/{twitch_uid}' if twitch_uid else 'emotes/BetterTTV/global'
        self.headers = {
            'Content-type' : 'application/json',
            'charset' : 'utf-8',
            'User-Agent' : 'Mozilla/5.0'
        }
        self.log = f'emotes/BetterTTV-{twitch_uid}@{today}.log' if twitch_uid else f'emotes/BetterTTV-global@{today}.log'
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
        os.makedirs(self.dir)
        pass
    
    async def get_json(self):
        async with (
            aiohttp.ClientSession() as session,
            aiofiles.open(self.log, 'w', encoding='utf-8') as log
        ):
            response = await session.get(url=self.api)
            response_json = await response.json(encoding='utf-8')
            log.write(response_json)
        if 'channelEmotes' in response_json and 'sharedEmotes' in response_json:
            emotes_json = response_json['channelEmotes'] + response_json['sharedEmotes']
        else:
            emotes_json = response_json
        for emote in emotes_json:
            emote['code'] = emote_code_legalization(emote['code'])
        return emotes_json
    
    async def download_emote(self, emote: dict):
        for x in [3, 2, 1]:
            async with (
                aiohttp.ClientSession() as session, 
                aiofiles.open(f"{self.dir}/{emote['code']}_{emote['id']}_{x}x.{emote['imageType']}", mode='wb') as file
            ):
                response = await session.get(url=f"{self.cdn}/{emote['id']}/{x}x")
                if response.status != 200:
                    print(f"{now()} Error: response status code NOT 200 for {emote['code']} {x}x")
                    continue
                response_read = await response.read()
                await file.write(response_read)
                print(f"{now()} {emote['code']} {x}x is downloaded.")
    
    async def keep_largest_qualified(self, emote: dict):
        match = [f'{self.dir}/{file}' for file in os.listdir(self.dir) if file.startswith(f"{emote['code']}_{emote['id']}")]
        qualified = [file for file in match if os.stat(file).st_size <= 262144]
        if qualified:
            largest = max(qualified, key=lambda file: os.stat(file).st_size)
            match.remove(largest)
        for file in match:
            os.remove(file)
            print(f"{now()} {file.split('/')[-1]} removed.")

class FrankerFaceZ():
    def __init__(self, twitch_uid: Union[int, str]) -> None:
        self.api = f'https://api.betterttv.net/3/cached/frankerfacez/users/twitch/{twitch_uid}'
        self.cdn = 'https://cdn.frankerfacez.com/emoticon'
        self.dir = f'emotes/FrankerFaceZ/{twitch_uid}'
        self.headers = {
            'Content-type' : 'application/json',
            'charset' : 'utf-8',
            'User-Agent' : 'Mozilla/5.0'
        }
        self.log = f'emotes/FrankerFaceZ-{twitch_uid}@{today}.log'
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
        os.makedirs(self.dir)
        pass

    async def get_json(self):
        async with (
            aiohttp.ClientSession() as session,
            aiofiles.open(self.log, 'w', encoding='utf-8') as log
        ):
            response = await session.get(url=self.api)
            response_json = await response.json(encoding='utf-8')
            await log.write(str(response_json))
        for emote in response_json:
            emote['code'] = emote_code_legalization(emote['code'])
        return response_json
    
    async def download_emote(self, emote: dict):
        for x in [4, 2, 1]:
            if not emote['images'][f'{x}x']:
                print(f"{now()} {emote['code']} {x}x not found!")
                continue
            async with (
                aiohttp.ClientSession() as session, 
                aiofiles.open(f"{self.dir}/{emote['code']}_{emote['id']}_{x}x.{emote['imageType']}", mode='wb') as file
            ):
                response = await session.get(url=emote['images'][f'{x}x'])
                if response.status != 200:
                    print(f"{now()} Error: response status code NOT 200 for {emote['code']} {x}x")
                    continue
                response_read = await response.read()
                await file.write(response_read)
                print(f"{now()} {emote['code']} {x}x is downloaded.")
                return

class SevenTV():
    def __init__(self, stv_uid: Union[int, str] = None) -> None:
        self.api = f'https://api.7tv.app/v2/users/{stv_uid}/emotes' if stv_uid else 'https://api.7tv.app/v2/emotes/global'
        self.cdn = 'https://cdn.7tv.app/emote'
        self.dir = f'emotes/7TV/{stv_uid}' if stv_uid else 'emotes/7TV/global'
        self.headers = {
            'Content-type' : 'application/json',
            'charset' : 'utf-8',
            'User-Agent' : 'Mozilla/5.0'
        }
        self.log = f"emotes/7TV-{stv_uid}@{today}.log" if stv_uid else f"emotes/7TV-global@{today}.log"
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
        os.makedirs(self.dir)
        pass

    async def get_json(self):
        async with (
            aiohttp.ClientSession() as session,
            aiofiles.open(self.log, 'w', encoding='utf-8') as log
        ):
            response = await session.get(url=self.api)
            response_json = await response.json(encoding='utf-8')
            await log.write(str(response_json))
        for emote in response_json:
            emote['name'] = emote_code_legalization(emote['name'])
        return response_json

    async def download_emote(self, emote: dict):
        for x in [4, 3, 2, 1]:
            if not str(x) in [list[0] for list in emote['urls']]:
                print(f"{now()} {emote['name']} {x}x not found!")
                continue
            async with (
                aiohttp.ClientSession() as session, 
                aiofiles.open(f"{self.dir}/{emote['name']}_{emote['id']}_{x}x.webp", mode='wb') as file
            ):
                response = await session.get(url=[list[1] for list in emote['urls'] if list[0]==str(x)][0])
                if response.status != 200:
                    print(f"{now()} Error: response status code NOT 200 for {emote['name']} {x}x")
                    continue
                response_read = await response.read()
                await file.write(response_read)
                print(f"{now()} {emote['name']} {x}x is downloaded.")
    
    def check_animated(self, emote_path: str):
        try:
            with Image.open(emote_path) as file:
                i = 0
                for frame in ImageSequence.Iterator(file):
                    i += 1
                if i > 1:
                    return True
                else:
                    return False
        except:
            print(f'{now()} Animated emote check failed for {emote_path}!')
            return False
    
    async def webp_to_gif(self, emote_path: str):
        with Image.open(emote_path) as emote:
            emote.info.pop('background', None)
            emote.save(emote_path.replace('.webp', '.gif'), save_all=True, disposal=2)
        os.remove(emote_path)
        print(f"{now()} {emote_path.split('/')[-1]} converted to gif.")
    
    async def keep_largest_qualified(self, emote: dict):
        match = [f'{self.dir}/{file}' for file in os.listdir(self.dir) if file.startswith(f"{emote['name']}_{emote['id']}")]
        qualified = [file for file in match if os.stat(file).st_size <= 262144]
        if qualified:
            largest = max(qualified, key=lambda file: os.stat(file).st_size)
            match.remove(largest)
        for file in match:
            os.remove(file)
            print(f"{now()} {file.split('/')[-1]} removed.")
    
class Discord():
    def __init__(self, js_token: Union[int, str], labo_array: list) -> None:
        self.api = 'https://discord.com/api'
        self.headers = {
            'authorization' : f'Bot {js_token}',
            'content-type': 'application/json'
        }
        self.array = labo_array
        pass

    async def get_gulid_emojis(self, guild_id: Union[int, str]):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            response = await session.get(url=f"{self.api}/guilds/{guild_id}/emojis")
            response_json = await response.json(encoding='utf-8')
        return response_json

    async def upload_emote(self, guild_id: Union[int, str], emote_name: str, emote_image_path: str):
        # uri = base64.b64encode(open(emote_path, "rb").read())
        # content = {
        #     'name' : emote_path.split('_')[0],
        #     'image' : f"data:image/{emote_path.split('.')[1]};base64,{uri.decode('utf-8')}"
        # }
        async with (
            aiohttp.ClientSession(headers=self.headers) as session,
            aiofiles.open(emote_image_path, 'rb') as file
        ):
            url = f"{self.api}/guilds/{guild_id}/emojis"
            uri = base64.b64encode(await file.read()).decode('utf-8')
            content = {
                "name": emote_name,
                "image": f"data:image/{emote_image_path.split('.')[-1]};base64,{uri}"
            }
            response = await session.post(url=url, data=json.dumps(content))
            if response.status == 429:
                response_json = await response.json(encoding='utf-8')
                retry_after = int(response_json['retry_after'])
                print(f"{now()} Upload {emote_name}: 429 - retrying after {retry_after}")
                await asyncio.sleep(round(retry_after/1000))
                await self.upload_emote(guild_id=guild_id, emote_name=emote_name, emote_path=emote_image_path)
            else:
                print(f"{now()} Post {emote_name}: {response.status}")
    
    async def delete_emote(self, guild_id: Union[int, str], emoji_name: str, emoji_id: Union[int, str]):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = f"{self.api}/guilds/{guild_id}/emojis/{emoji_id}"
            response = await session.delete(url=url)
            if response.status == 429:
                response_json = await response.json(encoding='utf-8')
                retry_after = int(response_json['retry_after'])
                print(f"{now()} Delete {emoji_name}: 429 - retrying after {retry_after}")
                await asyncio.sleep(round(retry_after/1000))
                await self.delete_emote(guild_id=guild_id, emoji_name=emoji_name, emoji_id=emoji_id)
            else:
                print(f"{now()} Delete {emoji_name}: {response.status}")


'''async def main():
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
    print('\033[90m'+u'\u2500'*32+'\033[0m')'''

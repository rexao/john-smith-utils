import asyncio
import base64
import datetime
import json
import os
import shutil
from typing import Any, Dict, List, Literal, Union

import aiofiles
import aiohttp
from PIL import Image, ImageSequence


now_str = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')

divider = '\033[90m'+u'\u2500'*32+'\033[0m'

def timestamp():
    return f"\033[90m{datetime.datetime.now().strftime('%H:%M:%S')}\033[0m"

async def sleep_before_next_minute():
    current_time = datetime.datetime.now()
    target_time = current_time.replace(second=0)+datetime.timedelta(minutes=1)
    # print((target_time-current_time).total_seconds())
    await asyncio.sleep((target_time-current_time).total_seconds())


class DiscordGuild():
    def __init__(
        self,
        js_token: str,
        id: int,
        emoji_limit: int = 50
    ) -> None:
        self.id = id
        self.emoji_limit = emoji_limit
        self.api = f'https://discord.com/api/guilds/{id}'
        self.headers = {
            'authorization' : f'Bot {js_token}',
            'content-type': 'application/json'
        }

    async def get_gulid_emojis(self, guild_id: int = None) -> List[Dict[str, Any]]:
        guild_id = guild_id if guild_id else self.id
        if not isinstance(guild_id, int):
            raise ValueError('Use get_gulid_array_emojis() instead.')
        async with aiohttp.ClientSession(headers=self.headers) as session:
            response = await session.get(url=f"{self.api}/emojis")
            return await response.json(encoding='utf-8')

    async def upload_emote(self, name: str, image: str, roles: List[int] = None) -> Dict[str, Any]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = f"{self.api}/emojis"
            content = {
                "name": name,
                "image": image,
                "roles": roles
            }
            response = await session.post(url=url, data=json.dumps(content))
            if response.status==201:
                print(f"{timestamp()} Post {name}: {response.status}")
                return await response.json(encoding='utf-8')
            elif response.status==429:
                response_json = await response.json(encoding='utf-8')
                retry_after = int(response_json['retry_after'])
                print(f"{timestamp()} Post {name}: {response.status} - retrying after {retry_after}")
                await asyncio.sleep(round(retry_after/1000))
                await self.upload_emote(name=name, image=image, roles=roles)
            else:
                print(f"{timestamp()} Post {name}: {response.status}")
                print(f"{await response.text()}")

            

    async def delete_emote(self, id: int, name: str = None) -> None:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = f"{self.api}/emojis/{id}"
            response = await session.delete(url=url)
            if response.status==204:
                print(f"{timestamp()} Delete {name if name else id}: {response.status}")
            elif response.status==429:
                response_json = await response.json(encoding='utf-8')
                retry_after = int(response_json['retry_after'])
                print(f"{timestamp()} Delete {name if name else id}: {response.status} - retrying after {retry_after}")
                await asyncio.sleep(round(retry_after/1000))
                await self.delete_emote(id=id, name=name)
            else:
                print(f"{timestamp()} Delete {name if name else id}: {response.status}")
                print(f"{await response.text()}")


class DiscordEmote():
    def __init__(
        self, *,
        name: str = None,
        roles: List[str] = None,
        id: int = None,
        require_colons: bool = None,
        managed: bool = None,
        animated: bool = None,
        available: bool = None,
        user: Dict[str, Any] = None
    ) -> None:
        self.name = name
        self.roles = roles
        self.id = id
        self.require_colons = require_colons
        self.managed = managed
        self.animated = animated
        self.available = available
        self.user = user

    def read_from_json(self, json: Dict[str, Any]):
        self.name = json['name']
        self.roles = json['roles']
        self.id = json['id']
        self.require_colons = json['require_colons']
        self.managed = json['managed']
        self.animated = json['animated']
        self.available = json['available']
        self.user = json['user']
        return self


class BetterTTV():
    def __init__(
        self,
        base_dir: str = 'emotes',
        twitch_uid: int = None
    ) -> None:
        self.cdn = "https://cdn.betterttv.net/emote"
        if twitch_uid:
            self.api = f"https://api.betterttv.net/3/cached/users/twitch/{twitch_uid}"
            self.dir = f"{base_dir}/BetterTTV/{twitch_uid}"
            self.archive_dir = f"{self.dir}-archived"
            self.log = f"{base_dir}/BetterTTV-{twitch_uid}@{now_str}.log"
            self.target = twitch_uid
        else:
            self.api = "https://api.betterttv.net/3/cached/emotes/global"
            self.dir = f"{base_dir}/BetterTTV/global"
            self.archive_dir = f"{self.dir}-archived"
            self.log = f"{base_dir}/BetterTTV-global@{now_str}.log"
            self.target = 'global'
        self.headers = {
            'Content-type' : 'application/json',
            'charset' : 'utf-8',
            'User-Agent' : 'Mozilla/5.0'
        }

        if os.path.exists(self.archive_dir):
            shutil.rmtree(self.archive_dir)
        if os.path.exists(self.dir):
            os.rename(self.dir, self.archive_dir)
        os.makedirs(self.dir)

    async def get_json(self) -> List[Dict[str, Any]]:
        async with (
            aiohttp.ClientSession() as session,
            aiofiles.open(self.log, 'w', encoding='utf-8') as log
        ):
            response = await session.get(url=self.api)
            response_json = await response.json(encoding='utf-8')
            await log.write(str(response_json))
            if 'channelEmotes' in response_json and 'sharedEmotes' in response_json:
                emotes_json = response_json['sharedEmotes']+response_json['channelEmotes']
                return emotes_json
            return response_json

class FrankFaceZ():
    def __init__(
        self, 
        base_dir: str = 'emotes',
        twitch_uid: int = None
    ) -> None:
        if not twitch_uid:
            raise AttributeError('FrankerFaceZ requires twitch_uid.')
        self.cdn = "https://cdn.frankerfacez.com/emoticon"
        self.api = f"https://api.betterttv.net/3/cached/frankerfacez/users/twitch/{twitch_uid}"
        self.dir = f"{base_dir}/FrankerFaceZ/{twitch_uid}"
        self.archive_dir = f"{self.dir}-archived"
        self.log = f"{base_dir}/FrankerFaceZ-{twitch_uid}@{now_str}.log"
        self.target = twitch_uid
        self.headers = {
            'Content-type' : 'application/json',
            'charset' : 'utf-8',
            'User-Agent' : 'Mozilla/5.0'
        }

        if os.path.exists(self.archive_dir):
            shutil.rmtree(self.archive_dir)
        if os.path.exists(self.dir):
            os.rename(self.dir, self.archive_dir)
        os.makedirs(self.dir)

    async def get_json(self) -> List[Dict[str, Any]]:
        async with (
            aiohttp.ClientSession() as session,
            aiofiles.open(self.log, 'w', encoding='utf-8') as log
        ):
            response = await session.get(url=self.api)
            response_json = await response.json(encoding='utf-8')
            await log.write(str(response_json))
            return response_json

class SevenTV():
    def __init__(
        self,
        base_dir: str = None,
        stv_uid: str = None
    ) -> None:
        self.cdn = "https://cdn.7tv.app/emote"
        if stv_uid:
            self.api = f"https://api.7tv.app/v2/users/{stv_uid}/emotes"
            self.dir = f"{base_dir}/7TV/{stv_uid}"
            self.archive_dir = f"{self.dir}-archived"
            self.log = f"{base_dir}/7TV-{stv_uid}@{now_str}.log"
            self.target = stv_uid
        else:
            self.api = "https://api.7tv.app/v2/emotes/global"
            self.dir = f"{base_dir}/7TV/global"
            self.archive_dir = f"{self.dir}-archived"
            self.log = f"{base_dir}/7TV-global@{now_str}.log"
            self.target = 'global'
        self.headers = {
            'Content-type' : 'application/json',
            'charset' : 'utf-8',
            'User-Agent' : 'Mozilla/5.0'
        }

        if os.path.exists(self.archive_dir):
            shutil.rmtree(self.archive_dir)
        if os.path.exists(self.dir):
            os.rename(self.dir, self.archive_dir)
        os.makedirs(self.dir)

    async def get_json(self) -> List[Dict[str, Any]]:
        async with (
            aiohttp.ClientSession() as session,
            aiofiles.open(self.log, 'w', encoding='utf-8') as log
        ):
            response = await session.get(url=self.api)
            response_json = await response.json(encoding='utf-8')
            await log.write(str(response_json))
            return response_json


class ThirdPartyEmote():
    def __init__(
        self, *,
        id: Union[int, str] = None,
        code: str = None,
        size: int = None,
        path: str = None,
        animated: bool = None
    ) -> None:
        self.id = id
        self.code = self.emote_code_legalization(code) if code else None
        self.size = size
        self.path = path
        self.animated = animated
        self.file_size = os.stat(path).st_size if path else None

    def emote_code_legalization(self, code: str) -> str:
        replacements = {
            ":": "colon",
            "&": "and",
            "+": "plus",
            "-": "minus",
        }
        for replacement in replacements:
            code = code.replace(replacement, replacements[replacement])
        return code[:32]

    def read_from_path(self, path: str):
        self.path = path
        tags = os.path.basename(path).split('.')[0]
        tags = tags.split('_')
        self.id, self.code, self.size = tags[0], tags[1], int(tags[2].replace('x', ''))
        self.animated = False if path.endswith('.png') else self.animated
        self.animated = True if path.endswith('.gif') else self.animated
        self.file_size = os.stat(path).st_size
        return self

    def delete(self):
        os.remove(self.path)
        print(f'{timestamp()} {self.code} {self.size}x removed.')
        return

    async def get_uri(self) -> str:
        async with aiofiles.open(self.path, 'rb') as file:
            b64 = base64.b64encode(await file.read()).decode('utf-8')
            uri = f"data:image/{self.path.split('.')[-1]};base64,{b64}"
        return uri

    def convert_webp_to_gif(self):
        if not self.path.endswith('.webp'):
            raise ValueError('File is not webp.')
        new_path = self.path.replace('.webp', '.gif')
        with Image.open(self.path) as emote:
            emote.info.pop('background', None)
            emote.save(new_path, save_all=True, disposal=2)
        os.remove(self.path)
        print(f'{timestamp()} {self.code} {self.size}x converted from webp to gif.')
        self.path, self.animated, self.file_size = new_path, True, os.stat(new_path).st_size
        return self

    def check_animated(self):
        try:
            with Image.open(self.path) as file:
                i = 0
                for frame in ImageSequence.Iterator(file):
                    i += 1
                self.animated = True if i>1 else False
                return self.animated
        except:
            print(f'{timestamp()} Animated emote check failed for {self.path}!')
            self.animated = False
            return self.animated

class BetterTTVEmote(ThirdPartyEmote):
    def __init__(
        self, *,
        id: str = None,
        code: str = None,
        imageType: Literal['gif', 'png'] = None,
        userId: str = None, user: Dict[str, Any] = None
    ) -> None:
        self.id = id
        self.code = self.emote_code_legalization(code) if code else None
        self.imageType = imageType
        self.userId, self.user = userId, user
        super().__init__()

    async def read_from_json(self, json: Dict[str, str]):
        self.id = json['id']
        self.code = self.emote_code_legalization(json['code'])
        self.imageType = json['imageType']
        if 'userId' in json:
            self.userId = json['userId']
        elif 'user' in json:
            self.user = json['user']
        else:
            raise ValueError("\"userId\" or \"user\" not found")
        return self

    async def download_emote(self, dir: str) -> List[ThirdPartyEmote]:
        return_list = []
        async with aiohttp.ClientSession() as session:
            for size in [3, 2, 1]:
                path = f"{dir}/{self.id}_{self.code}_{size}x.{self.imageType}"
                async with aiofiles.open(path, mode='wb') as file:
                    response = await session.get(url=f"https://cdn.betterttv.net/emote/{self.id}/{size}x")
                    if response.status != 200:
                        raise ValueError(f"{timestamp()} Error: response status code NOT 200 (is {response.status}) for {self.code} {size}x")
                    response_read = await response.read()
                    await file.write(response_read)
                    print(f"{timestamp()} {self.code} {size}x is downloaded.")
                return_list.append(ThirdPartyEmote().read_from_path(path=path))
        return return_list

class FrankerFaceZEmote(ThirdPartyEmote):
    def __init__(
        self, *,
        id: int = None,
        user: Dict[str, Any] = None,
        code: str = None,
        images: Dict[str, str] = None,
        imageType: Literal['gif', 'png'] = None
    ) -> None:
        self.id = id
        self.user = user
        self.code = self.emote_code_legalization(code) if code else None
        self.images = images
        self.imageType = imageType
        super().__init__()

    async def read_from_json(self, json: Dict[str, str]):
        self.id = json['id']
        self.user = json['user']
        self.code = self.emote_code_legalization(json['code'])
        self.images = json['images']
        self.imageType = json['imageType']
        return self

    async def download_emote(self, dir: str) -> List[ThirdPartyEmote]:
        return_list = []
        async with aiohttp.ClientSession() as session:
            for size in self.images:
                if not self.images[size]:
                    continue
                path = f"{dir}/{self.id}_{self.code}_{size}.{self.imageType}"
                async with aiofiles.open(path, mode='wb') as file:
                    response = await session.get(url=self.images[size])
                    if response.status != 200:
                        raise ValueError(f"{timestamp()} Error: response status code NOT 200 (is {response.status}) for {self.code} {size}x")
                    response_read = await response.read()
                    await file.write(response_read)
                    print(f"{timestamp()} {self.code} {size} is downloaded.")
                return_list.append(ThirdPartyEmote().read_from_path(path=path))
        return return_list

class SevenTVEmote(ThirdPartyEmote):
    def __init__(
        self, *,
        id: str = None,
        code: str = None,
        owner: Dict[str, Any] = None,
        visibility: int = None,
        visibility_simple: List[Any] = None,
        mime: str = None,
        status: int = None,
        tags: Any = None,
        width: List[List[int]] = None,
        height: List[List[int]] = None,
        urls: List[List[str]] = None
    ) -> None:
        self.id = id
        self.code = self.emote_code_legalization(code) if code else None
        self.owner = owner
        self.visibility = visibility
        self.visibility_simple = visibility_simple
        self.mime = mime
        self.status = status
        self.tags = tags
        self.width = width
        self.height = height
        self.urls = urls
        super().__init__()

    async def read_from_json(self, json: Dict[str, str]):
        self.id = json['id']
        self.code = self.emote_code_legalization(json['name'])
        self.owner = json['owner']
        self.visibility = json['visibility']
        self.visibility_simple = json['visibility_simple']
        self.mime = json['mime']
        self.status = json['status']
        self.tags = json['tags']
        self.width = json['width']
        self.height = json['height']
        self.urls = json['urls']
        return self

    async def download_emote(self, dir: str) -> List[ThirdPartyEmote]:
        return_list = []
        async with aiohttp.ClientSession() as session:
            for url_list in self.urls:
                size: str = url_list[0]
                url: str = url_list[1]
                path = f"{dir}/{self.id}_{self.code}_{size}.{url.split('.')[-1]}"
                response = await session.get(url=url)
                while response.status == 429:
                    print(f"{timestamp()} {self.code} {size}x download returned 429. (Sleeping before the next minute.)")
                    await sleep_before_next_minute()
                    response = await session.get(url=url)
                if response.status != 200:
                    raise ValueError(
                        f"{timestamp()} Error: response status code NOT 200 (is {response.status}) for {self.code} {size}x"+
                        f"\n{response.content}"
                    )
                response_read = await response.read()
                async with aiofiles.open(path, mode='wb') as file:
                    await file.write(response_read)
                    print(f"{timestamp()} {self.code} {size}x is downloaded.")
                return_list.append(ThirdPartyEmote().read_from_path(path=path))
        return return_list

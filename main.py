import asyncio
import base64
import json
import os
import re
import shutil
from typing import List

import aiofiles
import aiohttp
from PIL import Image

with open('config.json', 'r') as f:
    config: dict = json.load(f)


class Emote:
    def __init__(self, i, code, size, image_type, animated=None, image_url=None, file_path=None, file_size=None) -> None:
        self.id = i
        self.code = self._code_legalization(code)
        self.size = size
        self.image_type = image_type
        self.animated = animated

        self.image_url = image_url
        self.file_path = file_path
        self.file_size = file_size

        self.removed = False

    def _code_legalization(self, code):
        legalization_dict = {
            ":": "colon",
            "&": "and",
            "+": "plus",
            "-": "minus",
            "(": "",
            ")": ""
        }
        for entry in legalization_dict:
            code = code.replace(entry, legalization_dict[entry])
        return code[:32]

    async def download_image(self, session, image_url, folder_path):
        self.image_url = image_url
        self.file_path = f"{folder_path}/{self.id}_{self.code}_{self.size}x.{self.image_type}"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        print(self.image_url)
        async with session.get(self.image_url) as response:
            image_data = await response.read()
        async with aiofiles.open(self.file_path, 'wb') as f:
            await f.write(image_data)
        print(f"Downloaded: {os.path.join(*self.file_path.split('/'))}")
        self._webp_to_gif()
        self.file_size = os.stat(self.file_path).st_size

    def _webp_to_gif(self, file_path=None):
        self.file_path = file_path or self.file_path
        if not (self.file_path.endswith('.webp') and self.animated):
            return
        new_file_path = self.file_path.replace('.webp', '.gif')
        with Image.open(self.file_path) as emote:
            emote.info.pop('background', None)
            emote.save(new_file_path, save_all=True, disposal=2)
        os.remove(self.file_path)
        self.file_path, self.animated, = new_file_path, True

    def remove_image(self):
        if not self.file_path:
            raise AttributeError('File path is not specified yet')
        os.remove(self.file_path)
        self.removed = True

    @classmethod
    def from_file_name(cls, file_name: str):
        file_name, image_type = os.path.splitext(file_name)
        i, code, size = file_name.split('_')
        return cls(i, code, size, image_type)


class Bttv:
    def __init__(self, uid=None) -> None:
        self.api = config.get('bttv', {}).get(
            'api', 'https://api.betterttv.net/3/')
        self.cdn = config.get('bttv', {}).get(
            'cdn', 'https://cdn.betterttv.net/')
        self.provider = 'twitch'
        self.providerId = uid

        self._get_emotes = self._get_channel_emotes if uid else self._get_global_emotes

    async def _get_channel_emotes(self) -> List[dict]:
        async with aiohttp.ClientSession() as session:
            url = f"{self.api}/cached/users/{self.provider}/{self.providerId}"
            async with session.get(url) as response:
                data = await response.json()
                combined_emotes = data.get(
                    'channelEmotes', []) + data.get('sharedEmotes', [])
                return combined_emotes

    async def _get_global_emotes(self) -> List[dict]:
        async with aiohttp.ClientSession() as session:
            url = f"{self.api}/cached/emotes/global"
            async with session.get(url) as response:
                return await response.json()

    async def download_emotes(self):
        folder_path = f"emotes/BetterTTV/{self.providerId or 'global'}"
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
        os.makedirs(folder_path)
        emotes: List[Emote] = []
        emote_set = await self._get_emotes()
        async with aiohttp.ClientSession() as session:
            for obj in emote_set:
                i = obj.get('id')
                code = obj.get('code')
                imageType = obj.get('imageType')
                animated = obj.get('animated')

                for size in [1, 2, 3]:
                    emote = Emote(i, code, size, imageType, animated)
                    image_url = f"{self.cdn}/emote/{i}/{size}x"
                    await emote.download_image(session, image_url, folder_path)
                    emotes.append(emote)

        for i in [obj.get('id') for obj in emote_set]:
            qualified_variants = [
                emote for emote in emotes if emote.id == i and emote.file_size <= 262144]
            if not qualified_variants:
                for emote in [emote for emote in emotes if emote.id == i]:
                    emote.remove_image()
            else:
                best_variant = max(qualified_variants,
                                   key=lambda emote: emote.file_size)
                for emote in [emote for emote in emotes if emote.id == i]:
                    if emote.size != best_variant.size:
                        emote.remove_image()

        return emotes


class Ffz:
    def __init__(self, uid=None) -> None:
        self.api = config.get('ffz', {}).get(
            'api', 'https://api.frankerfacez.com')
        self.cdn = config.get('ffz', {}).get(
            'cdn', 'https://cdn.frankerfacez.com')
        self.twitchID = uid

        self._get_emotes = self._get_channel_emotes if self.twitchID else self._get_global_emotes

    async def _get_channel_emotes(self) -> List[dict]:
        async with aiohttp.ClientSession() as session:
            url = f"{self.api}/v1/rooms/id/{self.twitchID}"
            async with session.get(url) as response:
                data = await response.json()
                return data.get('emotes', [])

    async def _get_global_emotes(self) -> List[dict]:
        async with aiohttp.ClientSession() as session:
            url = f"{self.api}/v1/set/global"
            async with session.get(url) as response:
                data = await response.json()
                default_set_0 = data.get('default_sets')[0]
                emote_set = data.get('sets').get(str(default_set_0), {})
                return emote_set.get('emoticons', [])

    async def download_emotes(self):
        folder_path = f"emotes/FrankerFaceZ/{self.twitchID if self.twitchID else 'global'}"
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
        os.makedirs(folder_path)
        emotes = []
        emote_set = await self._get_emotes()
        async with aiohttp.ClientSession() as session:
            for obj in emote_set:
                i = obj.get('id')
                code = obj.get('name')
                imageType = 'png'
                animated = obj.get('animated', False)

                urls = obj.get('urls', {str(
                    size): f"https://cdn.frankerfacez.com/emote/{i}/{size}" for size in obj.get('sizes', [1, 2, 4])})
                for size in urls:
                    size = int(size)
                    emote = Emote(i, code, size, imageType, animated)
                    image_url = f"{urls[str(size)]}"
                    await emote.download_image(session, image_url, folder_path)
                    emotes.append(emote)

        for i in [obj.get('id') for obj in emote_set]:
            qualified_variants = [
                emote for emote in emotes if emote.id == i and emote.file_size <= 262144]
            if not qualified_variants:
                for emote in [emote for emote in emotes if emote.id == i]:
                    emote.remove_image()
            else:
                best_variant = max(qualified_variants,
                                   key=lambda emote: emote.file_size)
                for emote in [emote for emote in emotes if emote.id == i]:
                    if emote.size != best_variant.size:
                        emote.remove_image()

        return emotes


class Stv:
    def __init__(self, uid=None) -> None:
        self.api = config.get('stv', {}).get('api', 'https://7tv.io/v3')
        self.connection_platform = 'twitch'
        self.connection_id = uid

        self._get_emotes = self._get_channel_emotes if uid else self._get_global_emotes

    async def _get_channel_emotes(self) -> List[dict]:
        async with aiohttp.ClientSession() as session:
            url = f"{self.api}/users/{self.connection_platform}/{self.connection_id}"
            async with session.get(url) as response:
                data = await response.json()
                data = data.get('emote_set', {}).get('emotes', [])
                return data

    async def _get_global_emotes(self) -> List[dict]:
        async with aiohttp.ClientSession() as session:
            url = f"{self.api}/emote-sets/global"
            async with session.get(url) as response:
                data = await response.json()
                data = data.get('emotes', [])
                return data

    async def download_emotes(self):
        folder_path = f"emotes/7TV/{self.connection_id if self.connection_id else 'global'}"
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
        os.makedirs(folder_path)
        emotes = []
        emote_set = await self._get_emotes()
        async with aiohttp.ClientSession() as session:
            for obj in emote_set:
                i = obj.get('id')
                code = obj.get('name')
                data = obj.get('data')

                animated = data.get('animated')
                host_url = data.get('host', {}).get('url')
                files = data.get('host', {}).get('files', {})

                for f in files:
                    f_name = f.get('name', '')
                    size = re.search('\d+', f_name).group(0)
                    image_type = f.get('format', '').lower()
                    if image_type == 'avif':
                        continue
                    emote = Emote(i, code, size, image_type, animated)
                    image_url = f"https:{host_url}/{f_name}"
                    await emote.download_image(session, image_url, folder_path)
                    emotes.append(emote)

        for i in [obj.get('id') for obj in emote_set]:
            qualified_variants = [
                emote for emote in emotes if emote.id == i and emote.file_size <= 262144]
            if not qualified_variants:
                for emote in [emote for emote in emotes if emote.id == i]:
                    emote.remove_image()
            else:
                best_variant = max(qualified_variants,
                                   key=lambda emote: emote.file_size)
                for emote in [emote for emote in emotes if emote.id == i]:
                    if emote.size != best_variant.size:
                        emote.remove_image()

        return emotes


class DiscordGuild:
    def __init__(self, guild_id, emoji_limit, bot_token) -> None:
        self.api = config.get('discord', {}).get('api')
        self.guild_id = guild_id
        self.emoji_limit = emoji_limit
        self.headers = {
            'authorization': f'Bot {bot_token}',
            'content-type': 'application/json'
        }
        print(f"Processing guild {guild_id}")

    async def list_guild_emojis(self):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = f"{self.api}/guilds/{self.guild_id}/emojis"
            async with session.get(url) as response:
                return await response.json()

    async def create_guild_emoji(self, name, image_path, roles=None):
        async with aiofiles.open(image_path, 'rb') as f:
            image_b64 = base64.b64encode(await f.read()).decode('utf-8')
            image_uri = f"data:image/{image_path.split('.')[-1]};base64,{image_b64}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = f"{self.api}/guilds/{self.guild_id}/emojis"
            data = {
                "name": name,
                "image": image_uri,
                "roles": roles
            }
            async with session.post(url=url, data=json.dumps(data)) as response:
                if response.status == 201:
                    print(f"Post {name}: {response.status}")
                    return await response.json(encoding='utf-8')
                elif response.status == 429:
                    response_json = await response.json(encoding='utf-8')
                    retry_after = int(response_json['retry_after'])
                    print(
                        f"Post {name}: {response.status} - retrying after {retry_after}")
                    await asyncio.sleep(round(retry_after/1000))
                    return await self.create_guild_emoji(name=name, image_path=image_path, roles=roles)
                else:
                    print(f"Post {name}: {response.status}")
                    print(f"{await response.text()}")

    async def delete_guild_emoji(self, name, emoji_id):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = f"{self.api}/guilds/{self.guild_id}/emojis/{emoji_id}"
            async with session.delete(url=url) as response:
                if response.status == 204:
                    print(f"Delete {name}: {response.status}")
                    return await response.text(encoding='utf-8')
                elif response.status == 429:
                    response_json = await response.json(encoding='utf-8')
                    retry_after = int(response_json['retry_after'])
                    print(
                        f"Delete {name}: {response.status} - retrying after {retry_after}")
                    await asyncio.sleep(round(retry_after/1000))
                    return await self.delete_guild_emoji(name=name, emoji_id=emoji_id)
                else:
                    print(f"Delete {name}: {response.status}")
                    print(f"{await response.text()}")


async def main():
    archive_emotes: List[Emote] = []
    emote_dir = '/emotes/'
    if not os.path.exists(emote_dir):
        os.makedirs(emote_dir)
    for file_name in os.listdir(emote_dir):
        if os.path.isfile(os.path.join(emote_dir, file_name)):
            archive_emotes.append(Emote.from_file_name(file_name))

    twitch_uid = config.get('twitch', {}).get('uid', 0)
    bttv_global = Bttv()
    ffz_global = Ffz()
    stv_global = Stv()
    bttv_channel = Bttv(uid=twitch_uid)
    ffz_channel = Ffz(uid=twitch_uid)
    stv_channel = Stv(uid=twitch_uid)

    bttv_global_emotes = await bttv_global.download_emotes()
    ffz_global_emotes = await ffz_global.download_emotes()
    stv_global_emotes = await stv_global.download_emotes()
    bttv_channel_emotes = await bttv_channel.download_emotes()
    ffz_channel_emotes = await ffz_channel.download_emotes()
    stv_channel_emotes = await stv_channel.download_emotes()

    bot_token = config.get('discord', {}).get('bot_token')
    guild_array = config.get('discord', {}).get('guild_array')
    destination_guilds = config.get('discord', {}).get('destination_guilds')

    local_emotes = bttv_global_emotes+ffz_global_emotes+stv_global_emotes + \
        bttv_channel_emotes+ffz_channel_emotes+stv_channel_emotes
    local_static_emotes = [
        emote for emote in local_emotes
        if not emote.animated and not emote.removed
    ]
    local_animated_emotes = [
        emote for emote in local_emotes
        if emote.animated and not emote.removed
    ]
    local_modified_emotes = [
        emote for emote in local_emotes
        if emote.code in [emote.code for emote in archive_emotes] and
        emote.id not in [emote.id for emote in archive_emotes]
    ]

    for idx, guild in enumerate(guild_array):
        guild = DiscordGuild(guild.get('id'), 50, bot_token)
        guild_emojis = await guild.list_guild_emojis()
        guild_static_emojis = [
            emoji for emoji in guild_emojis if not emoji.get('animated')]
        guild_animated_emojis = [
            emoji for emoji in guild_emojis if emoji.get('animated')]
        new_static_emotes = local_static_emotes[idx*50:idx*50+50]
        new_animated_emotes = local_animated_emotes[idx*50:idx*50+50]

        for emoji in guild_static_emojis:
            name = emoji.get('name')
            if name not in [emote.code for emote in new_static_emotes]:
                await guild.delete_guild_emoji(name, emoji.get('id'))
        for emoji in guild_animated_emojis:
            name = emoji.get('name')
            if name not in [emote.code for emote in new_animated_emotes]:
                await guild.delete_guild_emoji(name, emoji.get('id'))
        for emote in new_static_emotes:
            if emote.code not in [emoji.get('name') for emoji in guild_static_emojis]:
                await guild.create_guild_emoji(emote.code, emote.file_path)
        for emote in new_animated_emotes:
            if emote.code not in [emoji.get('name') for emoji in guild_animated_emojis]:
                await guild.create_guild_emoji(emote.code, emote.file_path)
        for emote in local_modified_emotes:
            emoji_match = next(
                (emoji for emoji in guild_emojis if emoji.get('name') == emote.code), None)
            await guild.delete_guild_emoji(emoji_match.get('name'), emoji_match.get('id'))
            await guild.create_guild_emoji(emote.code, emote.file_path)

    local_emotes = ffz_channel_emotes+bttv_channel_emotes+stv_channel_emotes + \
        bttv_global_emotes+stv_global_emotes+ffz_global_emotes
    local_static_emotes = [
        emote for emote in local_emotes
        if not emote.animated and not emote.removed
    ]
    local_animated_emotes = [
        emote for emote in local_emotes
        if emote.animated and not emote.removed
    ]
    local_modified_emotes = [
        emote for emote in local_emotes
        if emote.code in [emote.code for emote in archive_emotes] and
        emote.id not in [emote.id for emote in archive_emotes]
    ]

    for guild in destination_guilds:
        guild = DiscordGuild(guild.get('id'), guild.get('guild'), bot_token)
        guild_emojis = await guild.list_guild_emojis()
        guild_static_emojis = [
            emoji for emoji in guild_emojis if not emoji.get('animated')]
        guild_animated_emojis = [
            emoji for emoji in guild_emojis if emoji.get('animated')]
        new_static_emotes = local_static_emotes[:guild.emoji_limit or 50]
        new_animated_emotes = local_animated_emotes[:guild.emoji_limit or 50]

        for emoji in guild_static_emojis:
            name = emoji.get('name')
            if name not in [emote.code for emote in new_static_emotes]:
                await guild.delete_guild_emoji(name, emoji.get('id'))
        for emoji in guild_animated_emojis:
            name = emoji.get('name')
            if name not in [emote.code for emote in new_animated_emotes]:
                await guild.delete_guild_emoji(name, emoji.get('id'))
        for emote in new_static_emotes:
            if emote.code not in [emoji.get('name') for emoji in guild_static_emojis]:
                await guild.create_guild_emoji(emote.code, emote.file_path)
        for emote in new_animated_emotes:
            if emote.code not in [emoji.get('name') for emoji in guild_animated_emojis]:
                await guild.create_guild_emoji(emote.code, emote.file_path)
        for emote in local_modified_emotes:
            emoji_match = next(
                (emoji for emoji in guild_emojis if emoji.get('name') == emote.code), None)
            await guild.delete_guild_emoji(emoji_match.get('name'), emoji_match.get('id'))
            await guild.create_guild_emoji(emote.code, emote.file_path)


if __name__ == '__main__':
    asyncio.run(main())

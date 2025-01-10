from pathlib import Path
from typing import Any

import nonebot
from nonebot.adapters import Bot

from zhenxun.models.ban_console import BanConsole
from zhenxun.models.bot_console import BotConsole
from zhenxun.models.group_console import GroupConsole
from zhenxun.models.level_user import LevelUser
from zhenxun.models.plugin_info import PluginInfo
from zhenxun.models.user_console import UserConsole
from zhenxun.services.cache import CacheRoot
from zhenxun.services.log import logger
from zhenxun.utils.enum import CacheType
from zhenxun.utils.platform import PlatformUtils

nonebot.load_plugins(str(Path(__file__).parent.resolve()))


driver = nonebot.get_driver()


@driver.on_bot_connect
async def _(bot: Bot):
    """将bot已存在的群组添加群认证

    参数:
        bot: Bot
    """
    if PlatformUtils.get_platform(bot) != "qq":
        return
    logger.debug(f"更新Bot: {bot.self_id} 的群认证...")
    group_list, _ = await PlatformUtils.get_group_list(bot)
    db_group_list = await GroupConsole.all().values_list("group_id", flat=True)
    create_list = []
    update_id = []
    for group in group_list:
        if group.group_id not in db_group_list:
            group.group_flag = 1
            create_list.append(group)
        else:
            update_id.append(group.group_id)
    if create_list:
        await GroupConsole.bulk_create(create_list, 10)
    else:
        await GroupConsole.filter(group_id__in=update_id).update(group_flag=1)
    logger.debug(
        f"更新Bot: {bot.self_id} 的群认证完成，共创建 {len(create_list)} 条数据，"
        f"共修改 {len(update_id)} 条数据..."
    )


@CacheRoot.new(CacheType.PLUGINS)
async def _(data: dict[str, PluginInfo] = {}, key: str | None = None):
    if data and key:
        if plugin := await PluginInfo.get_plugin(module=key):
            data[key] = plugin
    else:
        data_list = await PluginInfo.get_plugins()
        return {p.module: p for p in data_list}


@CacheRoot.updater(CacheType.PLUGINS)
async def _(data: dict[str, PluginInfo], key: str, value: Any):
    if value:
        data[key] = value
    elif plugin := await PluginInfo.get_plugin(module=key):
        data[key] = plugin


@CacheRoot.getter(CacheType.PLUGINS, result_model=PluginInfo)
async def _(data: dict[str, PluginInfo], module: str):
    result = data.get(module, None)
    if not result:
        result = await PluginInfo.get_plugin(module=module)
        if result:
            data[module] = result
    return result


@CacheRoot.new(CacheType.GROUPS)
async def _():
    data_list = await GroupConsole.all()
    return {p.group_id: p for p in data_list if not p.channel_id}


@CacheRoot.updater(CacheType.GROUPS)
async def _(data: dict[str, GroupConsole], key: str, value: Any):
    if value:
        data[key] = value
    elif group := await GroupConsole.get_group(group_id=key):
        data[key] = group


@CacheRoot.getter(CacheType.GROUPS, result_model=GroupConsole)
async def _(data: dict[str, GroupConsole], group_id: str):
    result = data.get(group_id, None)
    if not result:
        result = await GroupConsole.get_group(group_id=group_id)
        if result:
            data[group_id] = result
    return result


@CacheRoot.new(CacheType.BOT)
async def _():
    data_list = await BotConsole.all()
    return {p.bot_id: p for p in data_list}


@CacheRoot.updater(CacheType.BOT)
async def _(data: dict[str, BotConsole], key: str, value: Any):
    if value:
        data[key] = value
    elif bot := await BotConsole.get_or_none(bot_id=key):
        data[key] = bot


@CacheRoot.getter(CacheType.BOT, result_model=BotConsole)
async def _(data: dict[str, BotConsole], bot_id: str):
    result = data.get(bot_id, None)
    if not result:
        result = await BotConsole.get_or_none(bot_id=bot_id)
        if result:
            data[bot_id] = result
    return result


@CacheRoot.new(CacheType.USERS)
async def _():
    data_list = await UserConsole.all()
    return {p.user_id: p for p in data_list}


@CacheRoot.updater(CacheType.USERS)
async def _(data: dict[str, UserConsole], key: str, value: Any):
    if value:
        data[key] = value
    elif user := await UserConsole.get_user(user_id=key):
        data[key] = user


@CacheRoot.getter(CacheType.USERS, result_model=UserConsole)
async def _(data: dict[str, UserConsole], user_id: str):
    result = data.get(user_id, None)
    if not result:
        result = await UserConsole.get_user(user_id=user_id)
        if result:
            data[user_id] = result
    return result


@CacheRoot.new(CacheType.LEVEL)
async def _():
    return await LevelUser().all()


@CacheRoot.getter(CacheType.LEVEL, result_model=list[LevelUser])
def _(data_list: list[LevelUser], user_id: str, group_id: str | None = None):
    if not group_id:
        return [
            data for data in data_list if data.user_id == user_id and not data.group_id
        ]
    else:
        return [
            data
            for data in data_list
            if data.user_id == user_id and data.group_id == group_id
        ]


@CacheRoot.new(CacheType.BAN)
async def _():
    return await BanConsole.all()


@CacheRoot.getter(CacheType.BAN, result_model=list[BanConsole])
def _(data_list: list[BanConsole], user_id: str | None, group_id: str | None = None):
    if user_id:
        return (
            [
                data
                for data in data_list
                if data.user_id == user_id and data.group_id == group_id
            ]
            if group_id
            else [
                data
                for data in data_list
                if data.user_id == user_id and not data.group_id
            ]
        )
    if group_id:
        return [
            data for data in data_list if not data.user_id and data.group_id == group_id
        ]
    return None

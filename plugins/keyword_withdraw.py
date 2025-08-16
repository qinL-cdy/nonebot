from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent
from nonebot.rule import Rule
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="关键字撤回",
    description="检测并撤回包含特定关键字的群消息",
    usage="添加关键字: /add_keyword <关键词>\n删除关键字: /del_keyword <关键词>\n查看关键字列表: /list_keywords",
    type="application",
    homepage="https://github.com/your/repo",
    supported_adapters={"~onebot.v11"},
)

# 存储关键字的集合
keywords = {"csdx","人呢","敦➗","🐴","上号","сsdх"}

ban_user = {"384828033":"keyword",
            "492620247":"keyword",
            "605471601":"image",
            "2251738700":"keyword,image"}  # 可以添加更多用户

# 检查是否为群消息且不是自己发送的
def is_group_message(event: MessageEvent) -> bool:
    return isinstance(event, GroupMessageEvent) and not event.is_tome()

# 消息事件处理器
msg_handler = on_message(rule=Rule(is_group_message), priority=10, block=False)

def is_banned_user(event: GroupMessageEvent, type) -> bool:
    return str(event.user_id) in ban_user.keys() and type in ban_user[str(event.user_id)]

@msg_handler.handle()
async def handle_message(event: GroupMessageEvent, matcher: Matcher):
    if not is_banned_user(event, "keyword"):
        # 如果用户被禁言，直接返回
        return
    message = event.get_plaintext().strip()
    for keyword in keywords:
        if keyword in message:
            try:
                # 方法1：通过 nonebot.get_bot() 获取
                from nonebot import get_bot
                bot = get_bot()
                
                # 方法2：通过事件中的 self_id 获取（推荐）
                # bot = matcher.bot if hasattr(matcher, 'bot') else get_bot(str(event.self_id))
                
                await bot.delete_msg(message_id=event.message_id)
                # 可选：通知管理员
                # await bot.send_group_msg(
                #     group_id=event.group_id,
                #     message=f"检测到关键字 '{keyword}'，已撤回消息"
                # )
            except Exception as e:
                print(f"撤回消息失败: {e}")
            break
        
        
# 检测图片消息的规则
def is_image_message(event: GroupMessageEvent) -> bool:
    for segment in event.message:
        if segment.type == "image":
            return True
    return False


@msg_handler.handle()
async def handle_image(event: GroupMessageEvent):
    if not is_image_message(event):
        return
    if not is_banned_user(event, "image"):
        # 如果用户被禁言，直接返回
        return
    try:
        from nonebot import get_bot
        bot = get_bot()
        await bot.delete_msg(message_id=event.message_id)
    except Exception as e:
        print(f"禁言失败: {e}")

# 添加关键字命令
add_keyword = on_command("add_keyword", aliases={"添加关键字"}, permission=SUPERUSER)

@add_keyword.handle()
async def handle_add_keyword(event: MessageEvent, arg: Message = CommandArg()):
    keyword = arg.extract_plain_text().strip()
    if not keyword:
        await add_keyword.finish("请输入要添加的关键字")
    if keyword in keywords:
        await add_keyword.finish(f"关键字 '{keyword}' 已存在")
    keywords.add(keyword)
    await add_keyword.finish(f"已添加关键字: {keyword}")

# 删除关键字命令
del_keyword = on_command("del_keyword", aliases={"删除关键字"}, permission=SUPERUSER)

@del_keyword.handle()
async def handle_del_keyword(event: MessageEvent, arg: Message = CommandArg()):
    keyword = arg.extract_plain_text().strip()
    if not keyword:
        await del_keyword.finish("请输入要删除的关键字")
    if keyword not in keywords:
        await del_keyword.finish(f"关键字 '{keyword}' 不存在")
    keywords.remove(keyword)
    await del_keyword.finish(f"已删除关键字: {keyword}")

# 列出关键字命令
list_keywords = on_command("list_keywords", aliases={"关键字列表"}, permission=SUPERUSER)

@list_keywords.handle()
async def handle_list_keywords(event: MessageEvent):
    if not keywords:
        await list_keywords.finish("当前没有设置关键字")
    await list_keywords.finish("当前关键字列表:\n" + "\n".join(keywords))

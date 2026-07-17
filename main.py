"""
AstrBot 英文过滤插件 v2.0

功能描述：
- 拦截 AstrBot 输出（Bot 回复）中的英文字母
- 如果 Bot 回复包含英文，移除所有英文字母后输出
- 如果 Bot 回复不含英文，原样输出
- 如果清理失败，不做处理直接发送原消息

作者: user
版本: 2.0
日期: 2026-07-09
"""

from typing import Optional

import astrbot.api.message_components as Comp
from astrbot.api.star import Context, Star, register
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api import logger

from .constants import DEFAULT_REMOVE_SPACES, DEFAULT_LOG_FILTERED
from .utils import handle_errors, filter_english_text


@register("filter_english", "user", "拦截 AstrBot 输出中的英文字母", "2.0.0")
class FilterEnglishPlugin(Star):
    """英文过滤插件主类

    拦截 AstrBot 发送前的消息（Bot 回复），检测并清理其中的英文字母。
    只处理 Bot 的输出，不处理用户的输入消息。
    """

    def __init__(self, context: Context, config: dict = None):
        """初始化插件

        Args:
            context: AstrBot 上下文对象
            config: 插件配置字典
        """
        super().__init__(context)
        self.config = config or {}

        # 读取配置
        self.remove_spaces: bool = self.config.get("remove_spaces", DEFAULT_REMOVE_SPACES)
        self.log_filtered: bool = self.config.get("log_filtered", DEFAULT_LOG_FILTERED)

        logger.info("英文过滤插件 v2.0 初始化完成（仅拦截 Bot 输出）")

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        """拦截 Bot 发送前的消息，过滤其中的英文字母

        在消息发送前触发，修改 event.get_result().chain 中的文本内容。
        只处理 Bot 的回复消息，不处理用户输入。

        注意：这里不能使用 yield 发送消息，只能修改消息链。

        Args:
            event: 消息事件对象
        """
        result = event.get_result()
        if result is None:
            return

        chain = result.chain
        if not chain:
            return

        modified = False

        for i, component in enumerate(chain):
            # 只处理纯文本消息段
            if isinstance(component, Comp.Plain):
                original_text = component.text

                if not original_text:
                    continue

                # 过滤英文字母
                cleaned_text: Optional[str] = filter_english_text(
                    original_text, self.remove_spaces
                )

                # 清理失败：不做处理，保留原文
                if cleaned_text is None:
                    logger.warning(
                        f"[英文过滤] 清理失败，保留原文: \"{original_text}\""
                    )
                    continue

                # 如果文本被修改了（包含英文并被清理）
                if cleaned_text != original_text:
                    if self.log_filtered:
                        logger.info(
                            f"[英文过滤] 原文: \"{original_text}\" -> 过滤后: \"{cleaned_text}\""
                        )

                    # 修改消息链中的文本
                    chain[i] = Comp.Plain(text=cleaned_text)
                    modified = True

        # 如果有修改，更新消息链
        if modified:
            result.chain = chain

    @filter.command("✳fhelp")
    @handle_errors
    async def cmd_help(self, event: AstrMessageEvent):
        """查看插件帮助

        Args:
            event: 消息事件对象

        Yields:
            帮助信息
        """
        help_text = """📖 英文过滤插件帮助 v2.0
━━━━━━━━━━━━
🔧 功能说明:
拦截 AstrBot 输出（Bot 回复）中的英文字母，
如有则清理后输出，无英文则原样输出。

🎯 作用范围:
仅拦截 Bot 的回复消息，不影响用户输入。

⚠️ 失败处理:
如果清理过程中发生异常，不做任何处理，
直接发送原消息，确保消息不丢失。

⚙️ 配置项:
• remove_spaces: 清理后是否移除多余空格
• log_filtered: 是否在日志中记录过滤操作

💡 示例（Bot 回复）:
原文: Hello 你好 world
输出: 你好

原文: 纯中文内容
输出: 纯中文内容（不变）

原文: 123ABC456
输出: 123456
"""
        yield event.plain_result(help_text)

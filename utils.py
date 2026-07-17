"""
AstrBot 英文过滤插件 - 工具函数模块

提供文本过滤、错误处理等通用工具函数。
"""

import functools
import re
from typing import Callable, Any, AsyncGenerator, Optional

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent

from .constants import MessageEmoji, ENGLISH_PATTERN, WHITESPACE_PATTERN


def handle_errors(func: Callable) -> Callable:
    """统一错误处理装饰器

    捕获并处理函数执行过程中的各种异常，向用户返回友好的错误提示。

    Args:
        func: 被装饰的异步函数

    Returns:
        包装后的异步函数
    """
    @functools.wraps(func)
    async def wrapper(self, event: AstrMessageEvent, *args, **kwargs) -> AsyncGenerator[Any, None]:
        try:
            async for result in func(self, event, *args, **kwargs):
                yield result
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"[{func.__name__}] 执行失败 [{error_type}]: {e}", exc_info=True)
            yield event.plain_result(f"{MessageEmoji.ERROR} 插件执行出错，请联系管理员")
    return wrapper


def filter_english_text(text: str, remove_spaces: bool = True) -> Optional[str]:
    """过滤文本中的英文字母

    检测文本中是否包含英文字母，如果包含则移除所有英文字母，
    并根据配置决定是否清理多余空格。

    如果过滤过程中发生任何异常，返回 None 表示清理失败。

    Args:
        text: 原始文本
        remove_spaces: 是否移除清理后的多余空格

    Returns:
        过滤后的文本（如果原文不含英文则返回原文）；
        清理失败时返回 None
    """
    try:
        if not text:
            return text

        # 检查是否包含英文字母
        has_english = bool(ENGLISH_PATTERN.search(text))

        if not has_english:
            return text

        # 移除所有英文字母
        cleaned = ENGLISH_PATTERN.sub("", text)

        if remove_spaces:
            # 将连续空格合并为单个空格，并去除首尾空格
            cleaned = WHITESPACE_PATTERN.sub(" ", cleaned).strip()

        return cleaned

    except Exception as e:
        logger.error(f"[filter_english_text] 过滤失败: {e}", exc_info=True)
        return None

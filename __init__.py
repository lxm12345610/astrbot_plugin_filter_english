"""
AstrBot 英文过滤插件

拦截 AstrBot 输出（Bot 回复）中的英文字母。
清理失败时不做处理直接发送原消息。
"""

from .main import FilterEnglishPlugin

__all__ = ["FilterEnglishPlugin"]

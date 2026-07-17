"""
AstrBot 英文过滤插件 - 常量定义模块

定义插件使用的常量、正则表达式和配置项。
"""

import re
from typing import Pattern

# 版本信息
__version__ = "2.0.0"
__author__ = "user"

# 正则表达式
ENGLISH_PATTERN: Pattern = re.compile(r"[a-zA-Z]+")
WHITESPACE_PATTERN: Pattern = re.compile(r"\s+")

# 默认配置
DEFAULT_REMOVE_SPACES = True
DEFAULT_LOG_FILTERED = False

# 消息表情符号
class MessageEmoji:
    """消息表情符号"""
    ERROR = "❌"
    SUCCESS = "✅"
    WARNING = "⚠️"
    INFO = "ℹ️"

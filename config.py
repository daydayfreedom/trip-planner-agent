# config.py

import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
# 这行代码会自动查找当前目录或上级目录的.env文件
load_dotenv()

# --- 阿里云通义千问配置 ---
# 从环境变量获取DashScope API Key
# 如果环境变量中没有，就使用一个默认的提示性字符串
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# 检查Key是否存在，如果不存在则给出清晰的错误提示
if not DASHSCOPE_API_KEY:
    raise ValueError("错误：未找到 DASHSCOPE_API_KEY。\n请在项目根目录下创建 .env 文件，并添加 DASHSCOPE_API_KEY='你的Key'。")

# --- 高德地图配置 ---
# 从环境变量获取高德地图 API Key
AMAP_API_KEY = os.getenv("AMAP_API_KEY")

if not AMAP_API_KEY:
    raise ValueError("错误：未找到 AMAP_API_KEY。\n请在项目根目录下创建 .env 文件，并添加 AMAP_API_KEY='你的Key'。")

# 高德地图API的基础URL
AMAP_BASE_URL = "https://restapi.amap.com/v3"

# 你可以在这里添加其他全局配置
print("✅ 配置文件加载成功！")

# --- Tavily 搜索API配置 ---
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
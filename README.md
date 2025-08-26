# 🌏 路路通智能旅行社 (Trip Planner Agent)

一个基于大语言模型（LLM）和多Agent协作的智能旅行规划应用。它能像真人专家一样，从激发旅行灵感到生成分钟级的详细行程单，并提供可视化地图。

---

## 🔗 在线体验

**[>> 点击这里访问在线应用 <<](https://YOUR_STREAMLIT_APP_URL_HERE)**

*(部署上线后，请将 `YOUR_STREAMLIT_APP_URL_HERE` 替换成你的真实应用链接)*

## 📸 功能演示

*(建议：在这里放一张你的应用截图或一个简短的GIF动图，展示与Agent对话并生成计划的全过程。可以使用 `ScreenToGif` 或 `LICEcap` 等工具录制)*

## ✨ 主要功能

-   **双Agent协作**:
    -   🧭 **探索家Agent**: 负责与用户进行开放式对话，通过网络搜索激发灵感，并精确收集所有必要的旅行信息（如目的地、景点、酒店、交通等）。
    -   📅 **规划师Agent**: 接收“探索家”整理的结构化信息，调用地图API进行精确计算，生成一份详尽到分钟的旅行计划。
-   **实时数据驱动**: 所有地点坐标、两点间的交通方案和时间均通过调用**高德地图API**实时获取，确保计划的真实性和可行性。
-   **流式交互体验**: 对话和思考过程实时展示，让用户能清晰地看到Agent的“思考”过程，极大提升了用户体验。
-   **自然语言交互**: 用户全程只需通过自然语言与Agent对话，即可完成复杂的旅行规划任务。

## 🤖 核心架构

本项目采用了一种职责分离的多Agent架构，模拟了真实旅行社中“客户顾问”与“路线规划师”的协作流程。

```
用户输入模糊想法 (e.g., "我想去大连玩几天")
       │
       ▼
┌──────────────────┐
│  🧭 探索家Agent  │
│ - Tavily搜索信息 │
│ - 高德地图核实地点│
│ - 收集所有要素  │
└──────────────────┘
       │
       ▼ (输出结构化的JSON数据)
┌──────────────────┐
│  📅 规划师Agent  │
│ - 高德地图计算路线│
│ - 编排每日行程  │
│ - 生成行程单Markdown│
└──────────────────┘
       │
       ▼
最终输出: [详细行程单] + [交互式地图HTML]
```

## 🛠️ 技术栈

-   **前端**: [Streamlit](https://streamlit.io/)
-   **AI框架**: [LangChain](https://www.langchain.com/)
-   **大语言模型 (LLM)**: 阿里云通义千问 (qwen-plus)
-   **核心工具与API**:
    -   [高德地图Web服务API](https://lbs.amap.com/): 用于地点搜索(POI)、路线规划。
    -   [Tavily Search API](https://tavily.com/): 用于网络信息检索。
-   **配置管理**: `python-dotenv`

## 🚀 快速开始 (本地部署)

按照以下步骤在你的本地计算机上运行此项目。

### 1. 克隆仓库

```bash
git clone https://github.com/daydayfreedom/trip-planner-agent.git
cd trip-planner-agent
```

### 2. 安装依赖

建议在虚拟环境中安装，以避免包冲突。

```bash
# 创建虚拟环境 (可选但推荐)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装所有必要的库
pip install -r requirements.txt
```

*(如果还没有`requirements.txt`文件，请在本地项目目录中运行 `pip freeze > requirements.txt` 来生成它)*

### 3. 配置API Keys

项目运行需要多个API Key。

1.  在项目根目录下，创建一个名为 `.env` 的文件。
2.  复制以下内容到 `.env` 文件中，并替换成你自己的Key。

```env
# .env

# 阿里云通义千问 API Key (从 https://dashscope.console.aliyun.com/apiKey 获取)
DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 高德地图Web服务 API Key (从 https://console.amap.com/dev/key/app 获取)
AMAP_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Tavily Search API Key (从 https://app.tavily.com/ 获取)
TAVILY_API_KEY="tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**重要**: `.env` 文件已被添加到 `.gitignore` 中，它不会也**绝不能**被提交到GitHub仓库。

### 4. 运行应用

一切准备就绪！运行以下命令来启动Streamlit应用：

```bash
streamlit run app.py
```

应用将在你的浏览器中自动打开，通常地址为 `http://localhost:8501`。

## 📜 未来的想法

-   [ ] **Agent自动协作**: 实现从“探索家”到“规划师”的数据自动流转，无需用户干预。
-   [ ] **结构化输出**: 使用Pydantic强制Agent输出固定格式，提高系统稳定性。
-   [ ] **用户认证与历史记录**: 允许用户注册登录，并保存历史规划记录。
-   [ ] **多模态支持**: 允许用户上传图片来表达想去的地点。

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

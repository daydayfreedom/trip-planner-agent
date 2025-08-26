# app.py (最终流式处理版 - 解决KeyError: 'warnings'崩溃问题)

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

# 您的Agent创建函数
from explorer_agent_core import create_explorer_agent
from route_agent_core import create_route_agent

# --- 页面基础设置 ---
st.set_page_config(page_title="路路通智能旅行社", page_icon="🌏", layout="wide")
st.title("🌏 路路通智能旅行社")
st.caption("您的AI旅行探索与规划伙伴")

# --- Agent和状态初始化 ---
if "planner_agent" not in st.session_state:
    st.session_state.planner_agent = create_route_agent()
if "explorer_agent" not in st.session_state:
    st.session_state.explorer_agent = create_explorer_agent()

# 初始化聊天历史
if "explorer_messages" not in st.session_state:
    st.session_state.explorer_messages = [AIMessage(content="你好！我是“探索家”，有什么可以帮您发现的吗？")]
if "planner_messages" not in st.session_state:
    st.session_state.planner_messages = [AIMessage(content="你好！我是规划师“路路通”。请把您确定的旅行信息告诉我。")]

# --- 侧边栏 ---
with st.sidebar:
    st.header("选择对话伙伴")
    agent_choice = st.radio(
        "你想和谁对话？",
        ("探索家 (发现新灵感)", "规划师 (制定详细计划)"),
        key="agent_choice_radio"
    )
    st.info(
        "💡 **使用建议**:\n\n"
        "1. 先和“**探索家**”聊聊，找到心仪的目的地。\n\n"
        "2. 然后切换到“**规划师**”，开始详细规划。"
    )

# --- 主界面 ---
if "探索家" in agent_choice:
    st.header("与“探索家”的对话 🧭")
    messages_to_display = st.session_state.explorer_messages
    current_agent_key = "explorer"
    avatar = "🧭"
else:
    st.header("与“规划师”的对话 📅")
    messages_to_display = st.session_state.planner_messages
    current_agent_key = "planner"
    avatar = "📅"

# 渲染历史记录
for msg in messages_to_display:
    if isinstance(msg, AIMessage):
        st.chat_message("ai", avatar=avatar).write(msg.content)
    elif isinstance(msg, HumanMessage):
        st.chat_message("user", avatar="😊").write(msg.content)

# --- 核心交互逻辑：【修正为流式处理】 ---
if prompt := st.chat_input("请输入您的想法..."):
    history_to_update = st.session_state[f"{current_agent_key}_messages"]
    history_to_update.append(HumanMessage(content=prompt))
    st.chat_message("user", avatar="😊").write(prompt)

    agent_to_call = st.session_state[f"{current_agent_key}_agent"]

    with st.chat_message("ai", avatar=avatar):
        # 使用 st.write_stream 来优雅地处理流式输出
        def stream_generator():
            final_response = ""
            # 【关键】使用 agent.stream() 而不是 agent.invoke()
            stream = agent_to_call.stream({
                "input": prompt,
                "chat_history": history_to_update
            })

            # 遍历流中的每一个数据块
            for chunk in stream:
                # 从多种可能的结构中安全地提取文本内容
                content_to_yield = ""
                if "actions" in chunk:
                    for action in chunk["actions"]:
                        content_to_yield += f"🧠 **思考**: 决定调用工具 `{action.tool}`...\n\n"
                if "steps" in chunk:
                    for step in chunk["steps"]:
                        if hasattr(step, 'observation'):
                            content_to_yield += f"🛠️ **工具结果**: {str(step.observation)[:300]}...\n\n"
                if "messages" in chunk:
                    for message in chunk["messages"]:
                        content = message.content
                        if content:
                            final_response += content
                            content_to_yield += content

                if content_to_yield:
                    yield content_to_yield

            # 流程结束后，更新聊天历史
            if final_response:
                history_to_update.append(AIMessage(content=final_response))


        # 执行并渲染流
        st.write_stream(stream_generator)

# 打开方式  python -m streamlit run app.py
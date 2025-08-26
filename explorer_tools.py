# explorer_tools.py (V3 - 手动封装最终版)

from langchain_core.tools import tool
from tavily import TavilyClient  # 我们只使用这个最底层的、最稳定的导入
from config import TAVILY_API_KEY
from typing import List, Dict, Any

# 检查Tavily API Key是否存在
if not TAVILY_API_KEY:
    raise ValueError(
        "错误：未找到 TAVILY_API_KEY。\n"
        "请在 .env 文件中添加 TAVILY_API_KEY='tvly-xxxxxxxxxx'。"
    )

# 初始化底层的Tavily客户端
# 我们只在模块加载时初始化一次，以提高效率
try:
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    print("✅ 底层Tavily客户端初始化成功！")
except Exception as e:
    raise RuntimeError(f"无法初始化Tavily客户端，请检查API Key或网络。错误: {e}")


@tool
def tavily_search(query: str) -> List[Dict[str, Any]]:
    """
    一个网络搜索引擎工具，可以用来查询各种实时信息，如“xx有什么好玩的？”或“xx的背景知识”。
    这是探索未知信息时的首选工具。
    参数:
    - query: 你想要搜索的关键词或问题。
    返回: 一个包含多个搜索结果的列表，每个结果都是一个包含'title', 'url', 'content'的字典。
    """
    print(f"--- 🛠️ 调用手动封装的搜索工具 [tavily_search]: 查询 '{query}' ---")
    try:
        # 使用底层客户端执行搜索
        # search_depth='advanced' 可以获取更丰富的结果
        response = tavily_client.search(query=query, search_depth="advanced", max_results=5)

        # 我们只返回最重要的 'results' 部分
        results = response.get('results', [])

        if not results:
            print(f"--- ⚠️ [tavily_search] 警告: 查询 '{query}' 没有返回结果。---")
        else:
            # LangChain Agent能很好地处理字典列表
            print(f"--- ✅ [tavily_search] 成功: 查询 '{query}' 返回了 {len(results)} 条结果。---")

        return results

    except Exception as e:
        print(f"--- ❌ [tavily_search] 错误: 在执行搜索时发生异常: {e} ---")
        # 在工具出错时，返回一个包含错误信息的列表，让Agent知道发生了什么
        return [{"error": f"搜索时发生错误: {e}"}]


# 将我们手动创建的工具导出，给其他文件使用
# 注意：现在工具的名字是 tavily_search，而不是 tavily_tool
search_tool = tavily_search

# --- 用于独立测试工具的代码 ---
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("--- 正在以独立模式测试手动封装的搜索工具 ---")
    print("=" * 50)

    test_query = "大连一日游最佳路线推荐"
    print(f"测试查询: '{test_query}'\n")

    # 直接调用我们用@tool装饰的函数
    search_results = search_tool.invoke({"query": test_query})

    print("\n--- 工具返回的结果 ---")
    if search_results and not search_results[0].get("error"):
        for i, res in enumerate(search_results):
            print(f"\n[结果 {i + 1}]")
            print(f"  标题: {res.get('title')}")
            print(f"  链接: {res.get('url')}")
            print(f"  内容: {res.get('content', '')[:150]}...")
    else:
        print("测试未能获取到有效结果。")
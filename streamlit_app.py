import streamlit as st
import sys
import os
from io import StringIO
from datetime import datetime
from py1stauthor import Reader, Agent

# 多语言文本
TEXTS = {
    "zh": {
        "title": "🤖 py1stauthor Agent 实时演示",
        "config_header": "⚙️ 配置",
        "api_config": "API 配置",
        "arxiv_token": "arXiv API Token",
        "arxiv_token_help": "从 https://data.rag.ac.cn/register 获取",
        "llm_api_key": "LLM API Key",
        "model_config": "模型配置",
        "provider": "选择提供商",
        "model_name": "模型名称",
        "base_url": "Base URL",
        "agent_params": "Agent 参数",
        "max_llm_calls": "最大 LLM 调用次数",
        "temperature": "Temperature",
        "reset_button": "🔄 重置对话",
        "reset_success": "对话已重置！",
        "input_placeholder": "问我任何关于 arXiv 论文的问题...",
        "error_no_token": "❌ 请在侧边栏配置 arXiv API Token",
        "error_no_key": "❌ 请在侧边栏配置 LLM API Key",
        "thinking": "🤔 Agent 正在思考...",
        "final_answer": "### 📝 最终答案",
        "export_md": "📥 导出为 Markdown",
        "loaded_papers": "📄 已加载的论文",
        "title_label": "标题",
        "tokens_label": "Token数",
        "language": "语言",
    },
    "en": {
        "title": "🤖 py1stauthor Agent Demo",
        "config_header": "⚙️ Configuration",
        "api_config": "API Configuration",
        "arxiv_token": "arXiv API Token",
        "arxiv_token_help": "Get from https://data.rag.ac.cn/register",
        "llm_api_key": "LLM API Key",
        "model_config": "Model Configuration",
        "provider": "Select Provider",
        "model_name": "Model Name",
        "base_url": "Base URL",
        "agent_params": "Agent Parameters",
        "max_llm_calls": "Max LLM Calls",
        "temperature": "Temperature",
        "reset_button": "🔄 Reset Conversation",
        "reset_success": "Conversation reset!",
        "input_placeholder": "Ask me anything about arXiv papers...",
        "error_no_token": "❌ Please configure arXiv API Token in sidebar",
        "error_no_key": "❌ Please configure LLM API Key in sidebar",
        "thinking": "🤔 Agent is thinking...",
        "final_answer": "### 📝 Final Answer",
        "export_md": "📥 Export to Markdown",
        "loaded_papers": "📄 Loaded Papers",
        "title_label": "Title",
        "tokens_label": "Tokens",
        "language": "Language",
    }
}

# 页面配置
st.set_page_config(
    page_title="py1stauthor Agent",
    page_icon="🤖",
    layout="wide"
)

# 初始化会话状态
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'agent' not in st.session_state:
    st.session_state.agent = None

if 'language' not in st.session_state:
    st.session_state.language = 'zh'

# 获取当前语言文本
t = TEXTS[st.session_state.language]

# 自定义 CSS：启用代码块自动换行
st.markdown("""
<style>
/* 强制所有代码块自动换行 */
.stCodeBlock pre {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
}

.stCodeBlock code {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
}

/* status 容器中的代码 */
div[data-testid="stStatus"] pre,
div[data-testid="stStatus"] code {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
}

/* 历史消息中的代码 */
.stExpander pre,
.stExpander code {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
}
</style>
""", unsafe_allow_html=True)

# 标题和语言切换
col1, col2 = st.columns([4, 1])
with col1:
    st.title(t["title"])
with col2:
    if st.button(t["language"] + " 🌐", use_container_width=True):
        st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
        st.rerun()

st.markdown("---")

# 侧边栏配置
with st.sidebar:
    st.header(t["config_header"])
    
    # API配置
    st.subheader(t["api_config"])
    arxiv_token = st.text_input(
        t["arxiv_token"],
        value=os.getenv("ARXIV_TOKEN", ""),
        type="password",
        help=t["arxiv_token_help"]
    )
    
    llm_api_key = st.text_input(
        t["llm_api_key"],
        value=os.getenv("DEEPSEEK_API_KEY", ""),
        type="password"
    )
    
    # 模型选择
    st.subheader(t["model_config"])
    provider = st.selectbox(
        t["provider"],
        ["DeepSeek", "OpenAI", "OpenRouter", "Custom"]
    )
    
    if provider == "DeepSeek":
        model = "deepseek-chat"
        base_url = "https://api.deepseek.com"
    elif provider == "OpenAI":
        model = st.text_input(t["model_name"], value="gpt-4")
        base_url = "https://api.openai.com/v1"
    elif provider == "OpenRouter":
        model = st.text_input(t["model_name"], value="anthropic/claude-3-opus")
        base_url = "https://openrouter.ai/api/v1"
    else:
        model = st.text_input(t["model_name"], value="")
        base_url = st.text_input(t["base_url"], value="")
    
    # Agent参数
    st.subheader(t["agent_params"])
    max_llm_calls = st.slider(t["max_llm_calls"], 5, 50, 20)
    temperature = st.slider(t["temperature"], 0.0, 2.0, 0.7, 0.1)
    
    # 重置按钮
    if st.button(t["reset_button"], use_container_width=True):
        if 'agent' in st.session_state and st.session_state.agent is not None:
            st.session_state.agent.reset_papers()
            st.session_state.messages = []
            st.success(t["reset_success"])

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            # 显示答案
            st.markdown(message["content"])
            
            # 导出按钮
            if "content" in message:
                export_content = f"""# Query

{message.get("query", "N/A")}

## Answer

{message["content"]}

## Process

```
{message.get("process", "N/A")}
```

---
Generated by py1stauthor Agent
Date: {message.get("timestamp", "N/A")}
"""
                st.download_button(
                    label=t["export_md"],
                    data=export_content,
                    file_name=f"paper_analysis_{message.get('timestamp', 'export')}.md",
                    mime="text/markdown",
                    key=f"download_{message.get('timestamp', 'N/A')}"
                )
            
            # 查看推理过程
            if "process" in message:
                with st.expander("🔍 " + ("查看推理过程" if st.session_state.language == 'zh' else "View Reasoning Process"), expanded=False):
                    st.code(message["process"], language="text")
        else:
            st.markdown(message["content"])

# 用户输入
if question := st.chat_input(t["input_placeholder"]):
    # 检查必要的配置
    if not arxiv_token:
        st.error(t["error_no_token"])
        st.stop()
    
    if not llm_api_key:
        st.error(t["error_no_key"])
        st.stop()
    
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})
    
    # 初始化 Agent（如果尚未初始化）
    if 'agent' not in st.session_state or st.session_state.agent is None:
        try:
            with st.spinner("Initializing..." if st.session_state.language == 'en' else "正在初始化..."):
                reader = Reader(token=arxiv_token)
                st.session_state.agent = Agent(
                    api_key=llm_api_key,
                    model=model,
                    base_url=base_url,
                    reader=reader,
                    print_process=True,
                    stream=True,
                    max_llm_calls=max_llm_calls,
                    temperature=temperature
                )
        except Exception as e:
            st.error(f"❌ Initialization failed: {str(e)}" if st.session_state.language == 'en' else f"❌ 初始化失败: {str(e)}")
            st.stop()
    
    # 生成回答
    with st.chat_message("assistant"):
        # 重定向标准输出以捕获过程信息
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            # 使用 status 容器显示进度
            with st.status(t["thinking"], expanded=True) as status:
                # 创建一个固定的输出容器
                output_container = st.empty()
                
                # 获取 agent 引用（避免在线程中访问 session_state）
                agent = st.session_state.agent
                
                # 在后台线程中执行查询
                import threading
                result_container = {"answer": None, "error": None, "done": False}
                
                def run_query(agent_instance):
                    try:
                        result_container["answer"] = agent_instance.query(question)
                    except Exception as e:
                        result_container["error"] = e
                    finally:
                        result_container["done"] = True
                
                query_thread = threading.Thread(target=run_query, args=(agent,))
                query_thread.start()
                
                # 在主线程中轮询并更新输出（不会触发线程上下文错误）
                while not result_container["done"]:
                    current_output = mystdout.getvalue()
                    if current_output:
                        # 更新整个输出容器，保持格式一致
                        output_container.code(current_output, language="text")
                    import time
                    time.sleep(0.3)
                
                # 等待线程完成
                query_thread.join()
                
                # 检查错误
                if result_container["error"]:
                    raise result_container["error"]
                
                answer = result_container["answer"]
                
                # 恢复标准输出
                sys.stdout = old_stdout
                
                # 获取完整的过程输出
                process_output = mystdout.getvalue()
                
                # 最后一次更新显示完整输出
                output_container.code(process_output, language="text")
                
                status.update(label="✅ " + ("完成！" if st.session_state.language == 'zh' else "Done!"), state="complete")
            
            # 显示最终答案
            st.markdown(t["final_answer"])
            st.markdown(answer)
            
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 导出按钮
            export_content = f"""# Query

{question}

## Answer

{answer}

## Reasoning Process

```
{process_output}
```

---
Generated by py1stauthor Agent
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
            st.download_button(
                label=t["export_md"],
                data=export_content,
                file_name=f"paper_analysis_{timestamp}.md",
                mime="text/markdown",
                key=f"download_current_{timestamp}"
            )
            
            # 保存消息（包含推理过程，在历史记录中可以查看）
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "process": process_output,
                "query": question,
                "timestamp": timestamp
            })
                
        except Exception as e:
            sys.stdout = old_stdout
            st.error(f"❌ " + ("Error: " if st.session_state.language == 'en' else "出错了: ") + str(e))
            import traceback
            with st.expander("View Error Details" if st.session_state.language == 'en' else "查看详细错误"):
                st.code(traceback.format_exc())

# 显示已加载的论文
if 'agent' in st.session_state and st.session_state.agent is not None:
    loaded_papers = st.session_state.agent.get_loaded_papers()
    if loaded_papers:
        with st.sidebar:
            st.markdown("---")
            st.subheader(t["loaded_papers"])
            for paper_id, paper_info in loaded_papers.items():
                with st.expander(f"📖 {paper_id}", expanded=False):
                    st.write(f"**{t['title_label']}:** {paper_info.get('title', 'N/A')[:100]}...")
                    st.write(f"**{t['tokens_label']}:** {paper_info.get('token_count', 0)}")

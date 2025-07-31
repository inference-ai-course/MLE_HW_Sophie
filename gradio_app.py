import gradio as gr
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatOllama 
from openai import OpenAI
import traceback

# Initialize LangChain components
prompt = PromptTemplate.from_template(
    "What is the capital of {topic}?"
)
model = ChatOllama(model="llama2")
chain = (
    {"topic": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

# Initialize OpenAI client for Ollama
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama',  # required, but unused
)

def get_capital(country):
    """使用LangChain获取国家首都信息"""
    try:
        if not country.strip():
            return "请输入一个国家名称"
        
        result = chain.invoke(country)
        return f"问题: 什么是{country}的首都?\n回答: {result}"
    except Exception as e:
        return f"错误: {str(e)}\n请确保Ollama服务正在运行且llama2模型已安装"

def chat_with_assistant(message, history):
    """使用OpenAI兼容API与助手聊天"""
    try:
        if not message.strip():
            return history, ""
        
        # 构建消息历史
        messages = [{"role": "system", "content": "You are a helpful assistant. Please respond in Chinese when the user speaks Chinese, and in English when the user speaks English."}]
        
        # 添加历史对话
        for human, assistant in history:
            messages.append({"role": "user", "content": human})
            messages.append({"role": "assistant", "content": assistant})
        
        # 添加当前消息
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="llama2",
            messages=messages
        )
        
        assistant_response = response.choices[0].message.content
        history.append((message, assistant_response))
        
        return history, ""
    except Exception as e:
        error_msg = f"错误: {str(e)}\n请确保Ollama服务正在运行且llama2模型已安装"
        history.append((message, error_msg))
        return history, ""

def clear_chat():
    """清空聊天历史"""
    return [], ""

# 创建Gradio界面
with gr.Blocks(title="Ollama + LangChain Web UI", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 Ollama + LangChain Web UI")
    gr.Markdown("这个界面整合了LangChain和OpenAI兼容API来与Ollama模型交互")
    
    with gr.Tabs():
        # Tab 1: 首都查询 (LangChain)
        with gr.TabItem("🌍 首都查询 (LangChain)"):
            gr.Markdown("### 使用LangChain查询国家首都")
            gr.Markdown("输入国家名称，AI将告诉你它的首都")
            
            with gr.Row():
                with gr.Column(scale=3):
                    country_input = gr.Textbox(
                        label="国家名称",
                        placeholder="例如: 德国, 法国, 日本...",
                        lines=1
                    )
                with gr.Column(scale=1):
                    capital_btn = gr.Button("查询首都", variant="primary")
            
            capital_output = gr.Textbox(
                label="查询结果",
                lines=4,
                interactive=False
            )
            
            # 示例
            gr.Examples(
                examples=[["德国"], ["法国"], ["日本"], ["美国"], ["中国"]],
                inputs=[country_input],
                label="示例"
            )
            
            capital_btn.click(
                fn=get_capital,
                inputs=[country_input],
                outputs=[capital_output]
            )
            
            country_input.submit(
                fn=get_capital,
                inputs=[country_input],
                outputs=[capital_output]
            )
        
        # Tab 2: 智能助手 (OpenAI API)
        with gr.TabItem("💬 智能助手 (OpenAI API)"):
            gr.Markdown("### 与AI助手对话")
            gr.Markdown("支持连续对话，AI会记住之前的对话内容")
            
            chatbot = gr.Chatbot(
                label="对话历史",
                height=400,
                show_label=True
            )
            
            with gr.Row():
                with gr.Column(scale=4):
                    msg_input = gr.Textbox(
                        label="输入消息",
                        placeholder="在这里输入你的消息...",
                        lines=2
                    )
                with gr.Column(scale=1):
                    send_btn = gr.Button("发送", variant="primary")
                    clear_btn = gr.Button("清空对话", variant="secondary")
            
            # 示例对话
            gr.Examples(
                examples=[
                    ["你好，你是谁?"],
                    ["请告诉我关于机器学习的基础知识"],
                    ["什么是Python编程语言?"],
                    ["How are you today?"],
                    ["Explain quantum computing in simple terms"]
                ],
                inputs=[msg_input],
                label="示例对话"
            )
            
            send_btn.click(
                fn=chat_with_assistant,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input]
            )
            
            msg_input.submit(
                fn=chat_with_assistant,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input]
            )
            
            clear_btn.click(
                fn=clear_chat,
                outputs=[chatbot, msg_input]
            )
    
    # 底部信息
    gr.Markdown("---")
    gr.Markdown("""
    ### 📋 使用说明:
    1. **首都查询**: 使用LangChain框架，专门用于查询国家首都信息
    2. **智能助手**: 使用OpenAI兼容API，支持自由对话和连续上下文
    
    ### ⚙️ 前置要求:
    - 确保Ollama服务正在运行 (`ollama serve`)
    - 确保已安装llama2模型 (`ollama pull llama2`)
    
    ### 🚀 技术栈:
    - **前端**: Gradio
    - **后端**: LangChain + OpenAI客户端
    - **模型**: Ollama (llama2)
    """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

# -*- coding: utf-8 -*-
"""
Week 3 - Assignment: Voice Agent Development

A complete FastAPI voice chatbot that can:
1. Take audio input via HTTP
2. Transcribe audio to text (ASR) using Whisper
3. Generate response using OpenAI LLM
4. Convert response back to speech (TTS) using gTTS
5. Support 5-turn conversational memory

Requirements:
    pip install fastapi uvicorn openai-whisper gtts openai python-multipart

Environment Variables:
    OPENAI_API_KEY: Your OpenAI API key
"""

# 标准库导入
import os
import tempfile
import logging
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 第三方库导入
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import whisper
from gtts import gTTS
from openai import OpenAI
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量
conversation_history = []
asr_model = None
openai_client = None

class VoiceAssistant:
    """语音助手主类"""
    
    def __init__(self):
        self.conversation_history = []
        self.max_turns = 5
        
    def setup_models(self):
        """初始化模型和客户端"""
        global asr_model, openai_client
        
        try:
            # 初始化 Whisper 模型
            logger.info("Loading Whisper model...")
            asr_model = whisper.load_model("small")
            logger.info("Whisper model loaded successfully")
            
            # 初始化 OpenAI 客户端
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            
            openai_client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up models: {e}")
            raise
    
    def transcribe_audio(self, audio_bytes: bytes) -> str:
        """转录音频为文本"""
        try:
            # 创建临时文件保存音频数据
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_bytes)
                temp_audio_path = temp_file.name
            
            # 转录音频文件
            result = asr_model.transcribe(temp_audio_path)
            
            # 删除临时文件
            os.unlink(temp_audio_path)
            
            transcribed_text = result["text"].strip()
            logger.info(f"Transcribed text: {transcribed_text}")
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            # 清理临时文件
            try:
                if 'temp_audio_path' in locals():
                    os.unlink(temp_audio_path)
            except:
                pass
            raise HTTPException(status_code=500, detail=f"Audio transcription failed: {str(e)}")
    
    def generate_response(self, user_text: str) -> str:
        """使用 LLM 生成响应"""
        try:
            # 添加用户消息到历史记录
            self.conversation_history.append({"role": "user", "content": user_text})
            
            # 保持最近 5 轮对话
            messages = self.conversation_history[-self.max_turns * 2:]
            
            # 调用 OpenAI API
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7,
            )
            
            bot_response = response.choices[0].message.content
            
            # 添加助手响应到历史记录
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            
            logger.info(f"Generated response: {bot_response}")
            return bot_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise HTTPException(status_code=500, detail=f"Response generation failed: {str(e)}")
    
    def synthesize_speech(self, text: str, speed: float = 1.0) -> str:
        """将文本转换为语音
        
        Args:
            text: 要转换的文本
            speed: 语速倍率 (0.5-4.0)，1.0 为正常速度
        """
        try:
            import subprocess
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_path = temp_file.name
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as output_file:
                output_path = output_file.name
            
            # 使用 gTTS 生成初始语音
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_path)
            
            # 使用 ffmpeg 调整语速
            if speed != 1.0:
                # 构建 atempo 滤镜链
                # ffmpeg atempo 范围是 0.5-2.0，超出范围需要链接多个
                atempo_filters = []
                temp_speed = speed
                
                while temp_speed > 2.0:
                    atempo_filters.append("atempo=2.0")
                    temp_speed /= 2.0
                while temp_speed < 0.5:
                    atempo_filters.append("atempo=0.5")
                    temp_speed *= 2.0
                if temp_speed != 1.0:
                    atempo_filters.append(f"atempo={temp_speed}")
                
                # 构建 ffmpeg 命令
                filter_str = ",".join(atempo_filters) if atempo_filters else "anull"
                cmd = [
                    'ffmpeg', '-i', temp_path,
                    '-filter:a', filter_str,
                    '-y', output_path
                ]
                
                # 执行 ffmpeg
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.warning(f"ffmpeg failed: {result.stderr}, using original audio")
                    # 如果 ffmpeg 失败，使用原始音频
                    import shutil
                    shutil.move(temp_path, output_path)
                else:
                    # 删除临时文件
                    import os
                    os.unlink(temp_path)
            else:
                # 速度为 1.0，直接移动文件
                import shutil
                shutil.move(temp_path, output_path)
            
            logger.info(f"Generated audio file: {output_path} (speed: {speed}x)")
            return output_path
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

# 创建 FastAPI 应用
app = FastAPI(
    title="Voice Assistant API",
    description="A voice chatbot with ASR, LLM, and TTS capabilities",
    version="1.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建语音助手实例
assistant = VoiceAssistant()

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化模型"""
    try:
        assistant.setup_models()
        logger.info("Voice Assistant API started successfully")
    except Exception as e:
        logger.error(f"Failed to start Voice Assistant API: {e}")
        raise

@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "Voice Assistant API is running",
        "endpoints": {
            "chat": "/chat/ - POST with audio file",
            "health": "/health - GET health check",
            "history": "/history - GET conversation history"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "models_loaded": {
            "whisper": asr_model is not None,
            "openai": openai_client is not None
        }
    }

@app.get("/history")
async def get_conversation_history():
    """获取对话历史"""
    return {"conversation_history": assistant.conversation_history}

@app.post("/clear_history")
async def clear_conversation_history():
    """清除对话历史"""
    assistant.conversation_history = []
    return {"message": "Conversation history cleared"}

@app.post("/chat/")
async def chat_endpoint(
    file: UploadFile = File(...),
    speed: float = Form(1.25)  # 默认速度改为1.25
):
    """主要的聊天端点 - 处理音频输入并返回音频响应"""
    try:
        # 验证文件类型
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # 读取上传的音频文件
        audio_bytes = await file.read()
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # 步骤 1: ASR - 转录音频为文本
        user_text = assistant.transcribe_audio(audio_bytes)
        if not user_text:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
        # 步骤 2: LLM - 生成响应
        bot_text = assistant.generate_response(user_text)
        
        # 步骤 3: TTS - 将响应转换为语音
        # 验证速度参数范围
        if speed < 0.5 or speed > 4.0:
            speed = 1.0  # 超出范围使用默认值
            logger.warning(f"Speed {speed} out of range, using default 1.0")
        
        audio_path = assistant.synthesize_speech(bot_text, speed=speed)
        
        # 返回音频文件
        # 创建响应，不立即删除文件以避免问题
        return FileResponse(
            audio_path, 
            media_type="audio/wav",
            filename="response.wav"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def validate_environment():
    """验证环境变量和依赖"""
    errors = []
    
    # 检查 OpenAI API Key
    if not os.getenv('OPENAI_API_KEY'):
        errors.append("OPENAI_API_KEY environment variable is required")
    
    # 检查必要的包
    try:
        import whisper
        import gtts
        import openai
        import fastapi
        import uvicorn
    except ImportError as e:
        errors.append(f"Missing required package: {e}")
    
    if errors:
        for error in errors:
            logger.error(error)
        raise RuntimeError("Environment validation failed. Please check the errors above.")

if __name__ == "__main__":
    try:
        # 验证环境
        validate_environment()
        
        # 启动服务器
        logger.info("Starting Voice Assistant API server...")
        uvicorn.run(
            "week_3_assignment_voice_agent_development:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"\n错误: {e}")
        print("\n请确保:")
        print("1. 已安装所有依赖: pip install fastapi uvicorn openai-whisper gtts openai python-multipart")
        print("2. 已设置环境变量: export OPENAI_API_KEY='your-api-key'")
        print("3. 或者在 .env 文件中设置 OPENAI_API_KEY=your-api-key")
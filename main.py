# main.py
import streamlit as st
from gtts import gTTS
from io import BytesIO
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response
from starlette.concurrency import run_in_threadpool

# 配置全局设置
st.set_page_config(page_title="TTS 服务", page_icon="🎤")

# API 请求模型
class TTSRequest(BaseModel):
    text: str
    lang: str = "en"
    slow: bool = False

# 生成语音函数（同步版本）
def generate_tts_sync(text: str, lang: str, slow: bool = False) -> bytes:
    try:
        tts = gTTS(text=text, lang=lang, slow=slow)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception as e:
        raise ValueError(f"生成语音失败: {str(e)}")

# 网页界面
def web_interface():
    st.title("🎤 文本转语音服务")
    st.markdown("---")
    
    with st.expander("网页版使用说明", expanded=True):
        st.write("""
        1. 在下方输入要转换的文本
        2. 选择语言和语速
        3. 点击生成语音按钮
        4. 播放生成的语音并下载
        """)
    
    col1, col2 = st.columns(2)
    with col1:
        text = st.text_area("输入文本", height=150, 
                          placeholder="输入要转换为语音的文本...")
    
    with col2:
        lang = st.selectbox("选择语言", 
                           options=[ "zh-CN","en", "es", "fr", "ja", "ko"],
                           index=0)
        slow = st.checkbox("慢速模式")
        api_key = st.text_input("API 密钥（可选）", type="password")
    
    if st.button("✨ 生成语音", use_container_width=True):
        if not text.strip():
            st.error("请输入要转换的文本")
            return
            
        with st.spinner("生成语音中..."):
            try:
                # 使用同步版本的生成函数
                audio_bytes = generate_tts_sync(text, lang, slow)
                st.success("生成成功！")
                
                # 显示音频播放器
                st.audio(audio_bytes, format="audio/mpeg")
                
                # 添加下载按钮
                st.download_button(
                    label="下载音频",
                    data=audio_bytes,
                    file_name=f"tts_{lang}_{'slow' if slow else 'normal'}.mp3",
                    mime="audio/mpeg",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"生成失败: {str(e)}")
    
    st.markdown("---")
    with st.expander("API 使用说明"):
        st.write("""
        ### API 端点
        `POST /api/tts`

        ### 请求示例
        ```bash
        curl -X POST \\
          {url} \\
          -H "Content-Type: application/json" \\
          -d '{{"text": "Hello World", "lang": "en"}}'
        ```
        
        ### 请求参数
        ```json
        {{
            "text": "string",  // 必填，要转换的文本
            "lang": "string",   // 可选，语言代码（默认：en）
            "slow": boolean    // 可选，慢速模式（默认：false）
        }}
        ```
        
        ### 响应
        - 成功：返回 MP3 格式音频
        - 失败：返回 JSON 错误信息
        """.format(url=st.experimental_get_query_params().get("url", ["http://your-url/api/tts"])[0]))

if __name__ == "__main__":
    web_interface()

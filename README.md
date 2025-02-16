# API 端点
@st.experimental_route("/api/tts", methods=["POST"])
async def tts_endpoint(request: Request):
    try:
        data = await request.json()
        req = TTSRequest(**data)
        audio = await run_in_threadpool(generate_tts_sync, req.text, req.lang, req.slow)
        return Response(audio, media_type="audio/mpeg")
    
    except Exception as e:
        return Response(
            content={"error": str(e)},
            status_code=400,
            media_type="application/json"
        )

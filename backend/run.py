import asyncio
import sys
import uvicorn

# Kuralları Uvicorn çalışmadan ÖNCE biz koyuyoruz!
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

if __name__ == "__main__":
    # Uvicorn'u artık bu dosya üzerinden başlatacağız
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
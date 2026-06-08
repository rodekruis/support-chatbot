from __future__ import annotations

import uvicorn

from support_chatbot.main import app as application
from support_chatbot.settings import AppSettings

app = application


if __name__ == "__main__":
    settings = AppSettings()
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешенные источники
    allow_credentials=True,  # Разрешение на передачу cookies
    allow_methods=["*"],  # Разрешение всех HTTP-методов (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешение всех заголовков
)

@app.post("/auth/login")
async def read_root() -> dict:
    return {"message": "Welcome to your todo list."}


if __name__ == "__main__":
    # Запускаем приложение на хосте 0.0.0.0 и порту 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)

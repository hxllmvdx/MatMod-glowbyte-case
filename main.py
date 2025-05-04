import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Добавление CORS middleware для управления доступом к API
# origins - список разрешенных источников (доменов), которые могут обращаться к API
# "*" - разрешает доступ с любого источника (используется только для разработки)
origins = ["https://coal-calendar-mu.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешенные источники
    allow_credentials=True,  # Разрешение на передачу cookies
    allow_methods=["*"],  # Разрешение всех HTTP-методов (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешение всех заголовков
)

class WordInput(BaseModel):
    word: str

@app.post("/process")
def process_word(data: WordInput):
    return {"received_word": data.word}


if __name__ == "__main__":
    # Запускаем приложение на хосте 0.0.0.0 и порту 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)

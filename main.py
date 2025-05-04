import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from funcs import save_dataframe_to_db, create_work_table
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="https://coal-calendar-mu.vercel.app/",  # Разрешенные источники
    allow_credentials=True,  # Разрешение на передачу cookies
    allow_methods=["*"],  # Разрешение всех HTTP-методов (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешение всех заголовков
)
cur_tables = {'temperature': 0, 'supplies': 0, 'weather': 0}


class AddFilesRequest(BaseModel):
    """
    Модель для запроса на регистрацию.
    Поля:
    - email: Email пользователя (валидируется как EmailStr)
    - password: Пароль пользователя
    - nickname: Никнейм пользователя
    """
    temperature_csv_path: str
    supplies_csv_path: str
    fires_csv_path: str
    weather_csv_pathes: list


@app.post("/auth/login")
async def read_root(data: AddFilesRequest) -> dict:
    for i in cur_tables:
        cur_tables[i] += 1
    temperature_name = f'temperature_{cur_tables['temperature']}' if cur_tables['temperature'] > 0 else 'temperature'
    save_dataframe_to_db(data.temperature_csv_path, temperature_name, db_url)
    supplies_name = f'supplies_{cur_tables['supplies']}' if cur_tables['supplies'] > 0 else 'supplies'
    save_dataframe_to_db(data.supplies_csv_path, supplies_name, db_url)
    for i in data.weather_csv_pathes:
        weather_name = f'{i}_{cur_tables['weather']}' if cur_tables['weather'] > 0 else i
        save_dataframe_to_db(data.weather_csv_path, weather_name, db_url)

    create_work_table(db_url)
    return {"message": "All tables are saved."}


# Тестовый эндпоинт
# @app.get("/")
# async def root():
#     return {"message": "FastAPI backend is running"}


if __name__ == "__main__":
    db_url = 'postgresql://postgres:ZEcOwNDTbOQDjLHchZKyhEOeEOfnEcFW@switchyard.proxy.rlwy.net:44380/railway'
    uvicorn.run(app, host="0.0.0.0", port=8000)

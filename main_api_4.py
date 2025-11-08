import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from LPR_class import LPR_class
import httpx

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.sql_models import Base, Input_frame, Camera
from sqlalchemy.exc import SQLAlchemyError

MAX_RECORDS = 100
engine = create_engine("postgresql+psycopg2://app:secret@localhost:5432/app_db", echo=True)
Base.metadata.create_all(engine)

app = FastAPI()

# In-memory storage for active detections
detection_dict = {}

#запуск распознавания с UI
class StartDetectionRequest(BaseModel):
    source: str
    function_name: str

#остановка распознавания по зоне
class StopDetectionRequest(BaseModel):
    function_name: str

#сохранение результата в БД
class SendDetectionResults(BaseModel):
    image_base64: str
    detection_time: str
    camera_type: str
    license_plate: str

#отправка в номерофф на распознавание
class GetTextByImage(BaseModel):
    image: str

#Перед вставкой новой записи проверяете количество существующих и,
# если оно достигло лимита, удаляете или обновляете старые записи.
def add_or_replace_record(session: Session, new_record):
    # Проверяем текущее число записей
    count = session.query(Input_frame).count()
    if count >= MAX_RECORDS:
        # Удаляем старую запись (например, самую старую по datetime)
        oldest_record = session.query(Input_frame).order_by(Input_frame.datetime).first()
        if oldest_record:
            session.delete(oldest_record)
            session.commit()

    # Добавляем новую запись
    session.add(new_record)
    session.commit()

@app.post("/start-detection")
def start_detection(request: StartDetectionRequest):
    # получение источника, по идее 0 вебки у нас нет - но пусть будет)
    source = request.source
    if source == "0":
        source = int(source)

    # with Session(engine) as session:
    #     input = Input_frame(
    #         source=source,
    #         function_name= function_name
    #     )
    #     session.add_all([input])
    #     session.commit()

    # создаем класс моделиnpm
    detection = LPR_class(
        source=source,
        function_name=request.function_name
    )

    #раз у нас камера только на одну зону это въезд и выезд, то по этому параметру-ключу достаточно и сохранять
    detection_dict[request.function_name] = detection

    thread = threading.Thread(target=detection.run)
    thread.start()
    return {"message": "Detection started"}


@app.post("/stop-detection")
def stop_detection(request: StopDetectionRequest):
    print("stop_detection")
    function_name = request.function_name

    if function_name in detection_dict:
        detection = detection_dict[request.function_name]
        detection.stop()
        del detection_dict[request.function_name]
        print(f"Detection stopped for func ", request.function_name)
    else:
        raise HTTPException(status_code=404, detail=f"No active detection found for func {request.function_name}")


@app.post("/send-results")
async def send_results(payload: GetTextByImage):
    url = "http://127.0.0.1:8080/send-image"

    print(payload.dict())

    async with httpx.AsyncClient() as client:
        print("URL : ", url)
        response = await client.post(url, json=payload.dict(), timeout=600.0)
        response.raise_for_status()
        return response.text.strip("\"")


if __name__ == "__main__":
    #uvicorn.run(app, host="0.0.0.0", port=5000, reload=False)
    try:
        # Попытка открыть сессию
        with Session() as session:
            # Выполните простую команду, например, проверить наличие таблицы
            session.execute('SELECT 1')
        print("Подключение успешно!")
    except SQLAlchemyError as e:
        print(f"Ошибка подключения: {e}")
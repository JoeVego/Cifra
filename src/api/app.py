import threading
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import LPR_class
from src.sql import sql_queries
import base64
import redis
from datetime import datetime
import time
from fastapi.responses import StreamingResponse

MAX_RECORDS = 100
img_db_id = 0

app = FastAPI()
redis_server = redis.Redis(host='redis', port=6379, db=0)

# In-memory storage for active detections
detection_dict = {}


# запуск распознавания с UI
class StartDetectionRequest(BaseModel):
    source: str
    function_name: str


# остановка распознавания по зоне
class StopDetectionRequest(BaseModel):
    function_name: str


# сохранение результата в БД
class SendDetectionResults(BaseModel):
    image_base64: str
    detection_time: str
    camera_type: str
    license_plate: str


# отправка в номерофф на распознавание
class GetTextByImage(BaseModel):
    image: str


@app.post("/start-detection")
def start_detection(request: StartDetectionRequest):
    # получение источника, по идее 0 вебки у нас нет - но пусть будет)
    source = request.source
    if source == "0":
        source = int(source)

    # создаем класс модели
    detection = LPR_class.LPR_class(
        source=source,
        function_name=request.function_name,
        img_db_id=img_db_id
    )

    # раз у нас камера только на одну зону это въезд и выезд, то по этому параметру-ключу достаточно и сохранять
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
        global img_db_id
        img_db_id = detection.stop()
        del detection_dict[request.function_name]
        print(f"Detection stopped for func ", request.function_name)
    else:
        raise HTTPException(status_code=404, detail=f"No active detection found for func {request.function_name}")


@app.get("/get-results")
async def send_report_nn():
    select_res = sql_queries.get_detection_results()

    mapping = {
        "in": "въезд",
        "out": "выезд"
    }

    vue_results = [
        {'image': f"data:image/jpeg;base64,{base64.b64encode(item[4]).decode('utf-8')}",
         'date': item[2], 'source': mapping.get(item[3], item[3]), 'description': item[5]}
        for item in select_res
    ]

    return vue_results

@app.get("/get-report")
async def send_results_nn():
    select_res = sql_queries.get_report()

    client_mapping = {
        "new": "новый клиент",
        "existing": "существующий клиент"
    }

    status_mapping = {
        "new": "новая заявка",
        "exist": "без заявки"
    }

    vue_results = [
        {'client_type': client_mapping.get(item[0], item[0]),
         'status': status_mapping.get(item[1], item[1]),
         'counter': item[2]}
        for item in select_res
    ]

    return vue_results

@app.get("/get-time-report")
async def send_results_nn():
    select_res = sql_queries.get_time_report()

    client_mapping = {
        "new": "новый клиент",
        "existing": "существующий клиент"
    }

    vue_results = [
        {'licPlate': item[0],
         'time': item[1],
         'client_type': client_mapping.get(item[2], item[2])}
        for item in select_res
    ]

    return vue_results


def generate(camera_id):
    # Запоминаем дату начала стрима
    stream_start_date = datetime.now().date()

    while True:
        # Проверяем, не изменилась ли дата (наступил новый день)
        current_date = datetime.now().date()
        if current_date != stream_start_date:
            break

        current_frame = redis_server.get(f"{camera_id}_stream_frame")
        flag = int(redis_server.get(f"{camera_id}_stream_flag"))
        if flag == 1:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n')
        time.sleep(0.15)

@app.get("/video_feed/{camera_id}")
def video_feed(camera_id: str):
    stream_status = 1
    camera_id = 1

    if stream_status == 1:
        try:
            frame_generator = generate(camera_id)
            return StreamingResponse(frame_generator, media_type="multipart/x-mixed-replace;boundary=frame")
        except Exception as e:
            print(e)
    else:
        print("Stream is not available.")
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from src.model_list import model_list
from arch2.yolo_class import YoloClass

app = FastAPI()

# In-memory storage for active detections
detection_dict = {}

class StartDetectionRequest(BaseModel):
    source: str
    camera_id: str
    function_name: str
    skip_frames: Optional[int] = 1  # default to 1 if not provided


class StopDetectionRequest(BaseModel):
    camera_id: str


@app.post("/start_detection")
def start_detection(request: StartDetectionRequest):
    print("start_detection")
    source = request.source
    if source == "0":
        source = int(source)

    function_name = request.function_name
    if model_list.get(function_name) not in model_list:
        return "non-existant model, try another name"

    detection = YoloClass(
        source=source,
        camera_id=request.camera_id,
        function_name=request.function_name,
        skip_frames=request.skip_frames
    )
    detection_dict[request.camera_id] = detection

    thread = threading.Thread(target=detection.run)
    thread.start()

    return {"message": "Detection started"}


@app.post("/stop_detection")
def stop_detection(request: StopDetectionRequest):
    print("stop_detection")

    camera_id = request.camera_id
    if camera_id in detection_dict:
        detection = detection_dict[camera_id]
        detection.stop()
        del detection_dict[camera_id]
        return {"message": f"Detection stopped for Camera ID {camera_id}"}
    else:
        raise HTTPException(status_code=404, detail=f"No active detection found for Camera ID {camera_id}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
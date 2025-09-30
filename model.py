from ultralytics import YOLO

def get_yolo_track():
    """return model and preprocessing transform"""
    model = YOLO("yolo11n.pt")

    return model
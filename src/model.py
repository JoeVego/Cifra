from ultralytics import YOLO

def get_yolo_track():
    """return model and preprocessing transform"""
    model = YOLO("../data/weights/yolo11n.pt")

    return model

def get_yolo_track_by_path(path_in_folder):
    """return model and preprocessing transform"""
    model = YOLO("../" + path_in_folder)

    return model
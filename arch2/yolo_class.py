import cv2
from ultralytics import YOLO
from model_list import model_list


class YoloClass:
    def __init__(self, source, camera_id, function_name, skip_frames):
        self.videocapture = cv2.VideoCapture(source) #можно использовать путь к видео либо ртсп-ссылку
        self.model = YOLO(model_list[function_name]["model"])
        self.yolo_classes = model_list[function_name]["classes"]
        self.camera_id = camera_id
        self.skip_frames = skip_frames
        self.frame_counter = 0
        self.frame = None
        self.function_name = function_name
        self.detection_status = True
        print("init finished")

    def detect_cars(self):
        results = self.model(self.frame)

    def run(self):
        while self.detection_status == True:
            # Если не прошло skip_frames кадров, то пропускаем кадр
            if self.frame_counter % self.skip_frames != 0:
                self.videocapture.grab()
                self.frame_counter += 1
                continue
            
            ret, frame = self.videocapture.read()
            if ret:
                self.frame = frame
                self.frame_counter += 1

                if self.function_name == 'detect_cars':
                    self.detect_cars()
                    
                # show frame
                cv2.imshow(f'Camera {self.camera_id}', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("break from while loop")
                break
        self.videocapture.release()
        cv2.destroyAllWindows()
    
    def stop(self):
        self.detection_status = False

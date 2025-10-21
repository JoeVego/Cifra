import cv2
from ultralytics import YOLO
from src.model_list import model_list
from src.deteceted_object import deteceted_object
from src.prediction import bb_center_xy


class LPR_class:
    def __init__(self, source, camera_id, function_name, skip_frames):
        self.videocapture = cv2.VideoCapture(source)  # можно использовать путь к видео либо ртсп-ссылку
        self.model = YOLO(model_list[function_name]["model"])
        self.yolo_classes = model_list[function_name]["classes"]
        self.camera_id = camera_id
        self.skip_frames = skip_frames
        self.frame_counter = 0
        self.frame = None
        self.function_name = function_name
        self.detection_status = True
        self.track_id_old = None
        self.best_obj = deteceted_object(None, None, None, None)
        self.img_save_counter = 0
        print("init finished")

    def detect_lpr(self):
        preds = self.model.track(self.frame,
                                 conf = 0.3,
                                 persist=True)

        for results in preds:
            # Visualize the results on the frame
            annotated_frame = results.plot()
            cv2.imshow("YOLO Inference", annotated_frame)

            for result in results:
                x_center, y_center = bb_center_xy(result)
                # print(result.summary()[0].get('track_id'))

                if y_center > 120:
                    # получаем трек_ид его
                    track_id = result.summary()[0].get('track_id')

                    # если получаем первый кадр, т.е. такого трек_ид не было еще
                    if self.track_id_old is None:
                        # то присваиваем ему текущий айдишник
                        self.track_id_old = track_id
                        # сохраняем из списка резалта первый обнаруженный объект
                        if self.best_obj.get_track_id() is None:
                            self.best_obj = deteceted_object(result, track_id,
                                                             result.summary()[0].get('confidence'), annotated_frame)

                    # если у прогнозов одинаковый трек айди, то они сравниваются между собой
                    # оставляя прогноз, у которого больше уверенность
                    elif self.track_id_old == track_id:
                        if result.summary()[0].get('confidence') > self.best_obj.get_conf():
                            self.best_obj = deteceted_object(result, track_id,
                                                             result.summary()[0].get('confidence'), annotated_frame)

                    # когда перебраны все объекты по трек айди - то сохраняем лучший на диск
                    elif self.track_id_old != track_id:

                        # запись объекта на диск
                        result.save_crop("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\outs\\api_lp_5\\",
                                         "_" + str(track_id) + "_obj_" + str(self.img_save_counter)
                                         + "_conf_" + str(result.summary()[0].get('confidence')) + ".png")
                        self.img_save_counter = self.img_save_counter + 1

                        # а объект с новым трекером сохраняем для дальнейшего сравнения объекта
                        self.best_obj = deteceted_object(result, track_id,
                                                         result.summary()[0].get('confidence'), annotated_frame)
                        self.track_id_old = track_id

    def run(self):
        while self.detection_status == True:
            # Если не прошло skip_frames кадров, то пропускаем кадр
            if self.frame_counter % self.skip_frames != 0:
                self.videocapture.grab()
                self.frame_counter += 1
                continue

            success, frame = self.videocapture.read()
            if success:
                self.frame = frame
                self.frame_counter += 1

                if self.function_name == 'licence_plate_reg':
                    self.detect_lpr()

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("break from while loop")
                break
        self.videocapture.release()
        cv2.destroyAllWindows()

    def stop(self):
        self.detection_status = False

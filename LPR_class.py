import asyncio
import base64
import zoneinfo

import cv2
import httpx
from ultralytics import YOLO

from src.sql.sql_queries import insert_to_source, execute_sql, insert_frame
from src.model.deteceted_object import deteceted_object
from src.model.prediction import bb_center_xy
from datetime import datetime
from src.api import app
from src.image import get_bb_coords_by_result


class LPR_class:
    def __init__(self, source, function_name, img_db_id):
        print("source = ", source)
        self.videocapture = cv2.VideoCapture(source)  # можно использовать путь к видео либо ртсп-ссылку
        # self.model = YOLO(model_list[function_name]["model"]) - модель одна нет смысла другие веса или задачи брать !
        self.model = YOLO("/app/weights/0810_lp_ds_learn_yolo11_best.pt")
        # self.yolo_classes = model_list[function_name]["classes"] - как и объект - наша задача лишь номера !
        self.yolo_classes = [0]
        self.img_id = img_db_id
        self.lp_id = 0
        # он же тип записи
        #self.camera_type = camera_type
        # не вижу смысла давать пользователю выбирать сколько кадров скипать
        self.skip_frames = 2
        # счетчик для скипа кадров
        self.frame_counter = 0
        # текущий кадр
        self.frame = None
        # определение камера какую зону смотрит
        self.function_name = function_name
        self.detection_status = True
        # мои переменные для фильтрации всего что обнаружили
        self.track_id_old = None
        self.best_obj = deteceted_object(None, None, None, None)
        self.img_save_counter = 0
        self.source = source
        self.lic_plate_temp = ""
        self.is_temp_full = False
        self.frame_save_counter = 0
        print("init finished")

    def detect_lpr_2(self):
        # Инициализация истории для последних 5 результатов
        if not hasattr(self, 'track_last_results'):
            self.track_last_results = {}  # {track_id: [list of last results]}

        preds = self.model.track(self.frame,
                                 tracker="src\\model\\bytetrack.yaml",
                                 conf=0.3,
                                 iou=0.5,
                                 max_det=2,
                                 verbose=False,
                                 persist=True)

        for results in preds:
            annotated_frame = results.plot()
            cv2.imshow("AI licence plate recognition", annotated_frame)

            query_data = insert_to_source("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\camera_videos\\camera_records\\test3.mp4",
                                            "2024-04-27 15:30:00+03",
                                            "in",
                                          annotated_frame.tobytes())
            print("sql query data = ", query_data)
            # Теперь вызываем функцию execute_sql
            sql_result = asyncio.run(execute_sql(query_data))
            print(sql_result)

            for result in results:
                x_center, y_center = bb_center_xy(result)
                if y_center > 280 and x_center > 250:
                    track_id = result.summary()[0].get('track_id')
                    confidence = result.summary()[0].get('confidence')

                    # Инициализация для этого track_id
                    if track_id not in self.track_last_results:
                        self.track_last_results[track_id] = []

                    # Проверяем есть ли уже результат с таким track_id и более высоким conf
                    skip_new = False
                    for past_result in self.track_last_results[track_id]:
                        if past_result.get_track_id() == track_id:
                            if past_result.get_conf() >= confidence:
                                skip_new = True
                                break

                    if skip_new:
                        continue  # Пропускаем этот результат, т.к. есть более уверенный

                    # Создаем объект для текущего результата
                    current_obj = deteceted_object(result, track_id,
                                                   confidence, annotated_frame)

                    # Добавляем в историю
                    self.track_last_results[track_id].append(current_obj)
                    print("here !")
                    result.save_crop("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\outs\\api_lp_6\\",
                                     "_" + str(track_id) + "_obj_" + str(self.img_save_counter)
                                     + "_conf_" + str(result.summary()[0].get('confidence')) + ".png")
                    self.img_save_counter = self.img_save_counter + 1


                    # Ограничиваем длину истории до 5 элементов
                    if len(self.track_last_results[track_id]) > 10:
                        self.track_last_results[track_id].pop(0)

            # После обработки всех результатов за кадр, при необходимости, можно выбрать лучший результат
            # или выполнить другие действия.


    def detect_lpr(self):
        # получение предсказания модели - https://docs.ultralytics.com/ru/modes/predict/#inference-arguments
        preds = self.model.track(self.frame,
                                 tracker="/app/tracker/bytetrack.yaml",
                                 conf = 0.6,
                                 iou = 0.1,
                                 #imgsz = 640,
                                 #stream_buffer
                                 #agnostic_nms
                                 #stream
                                 max_det = 2,
                                 verbose = False,
                                 persist=True)

        for results in preds:

            # Visualize the results on the frame
            annotated_frame = results.plot()
            #настройка триггера с помощью визуализации
            #frame_with_box = print_line_cam1(annotated_frame)
            #cv2.imshow("AI licence plate recognition", annotated_frame)

            path_to_save = "/app/video/frame.jpg"
            #cv2.imwrite(path_to_save, annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            cv2.imwrite(path_to_save, annotated_frame)

            for result in results:
                x_center, y_center = bb_center_xy(result)
                # print(result.summary()[0].get('track_id'))

                #триггер
                if y_center > 280 and x_center > 250:

                    top_left_x, top_left_y, bottom_right_x, bottom_right_y = get_bb_coords_by_result(result)
                    bb_object = self.frame[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
                    #object_bytes = bb_object.tobytes()
                    #print("obj_bytes type = ", type(object_bytes))
                    #cv2.imshow("test", object)


                    base64_cv2_enc = cv2.imencode('.jpg', bb_object)
                    base64_cv2_enc = base64.b64encode(base64_cv2_enc[1]).decode('utf-8')
                    #print("\n base64 cv2 = ", base64_cv2_enc)

                    flag, cv2_enc_sql = cv2.imencode('.jpg', bb_object)
                    if flag:
                        cv2_enc_sql = cv2_enc_sql.tobytes()
                        #print("cv2_enc_sql type = ", type(cv2_enc_sql))
                    else:
                        print("encode error ! ")

                    lic_plate = ""
                    try:
                        lic_plate = httpx.post("http://172.20.0.5:8182/send-image", json={"image_base64": base64_cv2_enc}, timeout=600.0)
                        print("lic plate txt = ", lic_plate.text)
                        lic_plate = lic_plate.text.replace('"', '')
                    except httpx.ConnectError as e:
                        print(f"Не удалось подключиться: {e}")

                    if len(lic_plate) < 5:
                        continue

                    # print("temp = ", self.lic_plate_temp)
                    # print("lp = ", lic_plate)
                    # print("flag = ", self.is_temp_full)
                    if self.is_temp_full:
                        if lic_plate == self.lic_plate_temp:
                            continue
                        elif lic_plate != self.lic_plate_temp:
                            self.lic_plate_temp = lic_plate
                    else:
                        self.lic_plate_temp = lic_plate
                        self.is_temp_full = True


                    #print("img_id before = ", self.img_id)
                    query, params = insert_to_source(
                        self.img_id,
                        self.source,
                        datetime.now(zoneinfo.ZoneInfo("Asia/Dubai")).strftime("%Y-%m-%d %H:%M:%S"),
                        #"in",
                        str(self.function_name),
                        cv2_enc_sql,
                        lic_plate)
                    sql_result = execute_sql(query, params)
                    print(sql_result)
                    self.img_id = self.img_id + 1
                    #print("img_id after = ", self.img_id)

                    # получаем трек_ид объекта на изображении
                    track_id = result.summary()[0].get('track_id')

                    # Если получаем первый кадр, т.е. такого трек_ид не было еще
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
                        now = datetime.now()
                        #запись объекта на диск
                        result.save_crop("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\outs\\api_lp_5\\",
                                         "_" + str(track_id) + "_obj_" + str(self.img_save_counter)
                                         + "_conf_" + str(result.summary()[0].get('confidence')) + ".png")
                        self.img_save_counter = self.img_save_counter + 1

                        # а объект с новым трекером сохраняем для дальнейшего сравнения объекта
                        self.best_obj = deteceted_object(result, track_id,
                                                         result.summary()[0].get('confidence'), annotated_frame)
                        self.track_id_old = track_id

    def run(self):
        #если обнарудение не остановлено
        while self.detection_status == True:
            # пропуск кадров
            if self.frame_counter % self.skip_frames != 0:
                self.videocapture.grab()
                self.frame_counter += 1
                continue

            # получаем кадр
            success, frame = self.videocapture.read()
            if success:
                self.frame = frame
                self.frame_counter += 1

                #передаем в модель
                self.detect_lpr()
                #asyncio.run(self.detect_lpr())
                # self.detect_lpr_2()

                # прерываем
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("break from while loop")
                break
        #освобождение ресурсов
        self.videocapture.release()
        cv2.destroyAllWindows()

    #остановка
    def stop(self):
        self.detection_status = False
        return self.img_id

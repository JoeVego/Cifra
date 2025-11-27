import base64
import zoneinfo
import cv2
import httpx
from ultralytics import YOLO
import redis

from src.sql.sql_queries import insert_to_source, execute_sql
from src.model.deteceted_object import deteceted_object
from src.model.prediction import bb_center_xy
from datetime import datetime
from src.image import get_bb_coords_by_result


class LPR_class:
    def __init__(self, source, function_name, img_db_id):
        print("source = ", source)
        self.videocapture = cv2.VideoCapture(source)  # можно использовать путь к видео либо ртсп-ссылку
        self.model = YOLO("/app/weights/0810_lp_ds_learn_yolo11_best.pt")
        self.yolo_classes = [0]
        self.img_id = img_db_id
        self.lp_id = 0
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
        #self.track_id_old = None
        #self.best_obj = deteceted_object(None, None, None, None)
        #self.img_save_counter = 0
        self.source = source
        self.lic_plate_temp = ""
        self.is_temp_full = False
        self.redis_server = redis.Redis(host='redis', port=6379, db=0)
        self.lic_plate_text = ""
        print("init finished")

    # def detect_lpr_2(self):
    #     # Инициализация истории для последних 5 результатов
    #     if not hasattr(self, 'track_last_results'):
    #         self.track_last_results = {}  # {track_id: [list of last results]}
    #
    #     preds = self.model.track(self.frame,
    #                              tracker="src\\model\\bytetrack.yaml",
    #                              conf=0.3,
    #                              iou=0.5,
    #                              max_det=2,
    #                              verbose=False,
    #                              persist=True)
    #
    #     for results in preds:
    #         annotated_frame = results.plot()
    #         #cv2.imshow("AI licence plate recognition", annotated_frame)
    #
    #         query_data = insert_to_source("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\camera_videos\\camera_records\\test3.mp4",
    #                                         "2024-04-27 15:30:00+03",
    #                                         "in",
    #                                       annotated_frame.tobytes())
    #         print("sql query data = ", query_data)
    #         # Теперь вызываем функцию execute_sql
    #         sql_result = asyncio.run(execute_sql(query_data))
    #         print(sql_result)
    #
    #         for result in results:
    #             x_center, y_center = bb_center_xy(result)
    #             if y_center > 280 and x_center > 250:
    #                 track_id = result.summary()[0].get('track_id')
    #                 confidence = result.summary()[0].get('confidence')
    #
    #                 # Инициализация для этого track_id
    #                 if track_id not in self.track_last_results:
    #                     self.track_last_results[track_id] = []
    #
    #                 # Проверяем есть ли уже результат с таким track_id и более высоким conf
    #                 skip_new = False
    #                 for past_result in self.track_last_results[track_id]:
    #                     if past_result.get_track_id() == track_id:
    #                         if past_result.get_conf() >= confidence:
    #                             skip_new = True
    #                             break
    #
    #                 if skip_new:
    #                     continue  # Пропускаем этот результат, т.к. есть более уверенный
    #
    #                 # Создаем объект для текущего результата
    #                 current_obj = deteceted_object(result, track_id,
    #                                                confidence, annotated_frame)
    #
    #                 # Добавляем в историю
    #                 self.track_last_results[track_id].append(current_obj)
    #                 print("here !")
    #                 result.save_crop("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\outs\\api_lp_6\\",
    #                                  "_" + str(track_id) + "_obj_" + str(self.img_save_counter)
    #                                  + "_conf_" + str(result.summary()[0].get('confidence')) + ".png")
    #                 self.img_save_counter = self.img_save_counter + 1
    #
    #
    #                 # Ограничиваем длину истории до 5 элементов
    #                 if len(self.track_last_results[track_id]) > 10:
    #                     self.track_last_results[track_id].pop(0)

    def detect_lpr(self):
        # получение предсказания модели - https://docs.ultralytics.com/ru/modes/predict/#inference-arguments
        preds = self.model.track(self.frame,
                                 tracker="/app/tracker/bytetrack.yaml",
                                 conf = 0.5,
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

            for result in results:
                x_center, y_center = bb_center_xy(result)
                #print("Проверка трек айди = ", result.summary()[0].get('track_id'))

                # для разных камер разный триггер
                # if self.function_name == "зона въезда":
                #     trigger_y = 280
                #     trigger_x = 250
                # elif self.function_name == "зона выезда":
                #     trigger_y = 280
                #     trigger_x = 250

                #триггер
                if y_center > 280 and x_center > 250:
                    #получаю область ББ обнаруенного объекта
                    top_left_x, top_left_y, bottom_right_x, bottom_right_y = get_bb_coords_by_result(result)
                    bb_object = self.frame[top_left_y:bottom_right_y, top_left_x:bottom_right_x]

                    #кодировавка
                    base64_cv2_enc = cv2.imencode('.jpg', bb_object)
                    base64_cv2_enc = base64.b64encode(base64_cv2_enc[1]).decode('utf-8')

                    cv2_bb_encode_flag, cv2_enc_sql = cv2.imencode('.jpg', bb_object)
                    if cv2_bb_encode_flag:
                        cv2_enc_sql = cv2_enc_sql.tobytes()
                    else:
                        print("encode error ! ")

                    #передача в NN
                    try:
                        lic_plate_resp = httpx.post("http://172.20.0.3:8182/send-image", json={"image_base64": base64_cv2_enc}, timeout=600.0)
                        print("lic plate txt = ", lic_plate_resp.text)
                        self.lic_plate_text = lic_plate_resp.text.replace('"', '')
                    except httpx.ConnectError as e:
                        print(f"Не удалось подключиться: {e}")

                    #фильтр если номер короткий
                    if len(self.lic_plate_text) < 5:
                        continue

                    # исключаем дубли
                    if self.is_temp_full:
                        if self.lic_plate_text == self.lic_plate_temp:
                            continue
                        elif self.lic_plate_text != self.lic_plate_temp:
                            self.lic_plate_temp = self.lic_plate_text
                    else:
                        self.lic_plate_temp = self.lic_plate_text
                        self.is_temp_full = True

                    # сохраняем в бд
                    query, params = insert_to_source(
                        str(self.img_id) + "_" + str(self.function_name),
                        self.source,
                        datetime.now(zoneinfo.ZoneInfo("Asia/Dubai")).strftime("%Y-%m-%d %H:%M:%S"),
                        str(self.function_name),
                        cv2_enc_sql,
                        self.lic_plate_text)
                    sql_result = execute_sql(query, params)
                    print(sql_result)
                    self.img_id = self.img_id + 1

            return cv2.resize(annotated_frame, (1115, 627))

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
                camera_id = 1
                self.frame = frame

                #передаем в модель
                stream_frame = self.detect_lpr()

                (self.stream_flag, encoded_frame) = cv2.imencode(".jpg", stream_frame)
                self.stream_frame = encoded_frame.tobytes()

                self.redis_server.set(f"{camera_id}_stream_frame", self.stream_frame)

                if self.stream_flag == True:
                    self.redis_server.set(f"{camera_id}_stream_flag", 1)
                else:
                    self.redis_server.set(f"{camera_id}_stream_flag", 0)

                self.frame_counter += 1

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

from ultralytics import YOLO
import cv2

from model import get_yolo_track
from image import line_dot1, line_dot2, line_color, line_thickness
from image import zone_limit_x, zone_limit_y, img_save
from prediction import bb_center_xy, desciption, get_id_coords, get_obj_trackId
from deteceted_object import deteceted_object

# пропуск кадров
PROCESS_EVERY_N_FRAME = 5
# счетчик кадров
frame_counter = 0
# ищем только класс грузовики = 7
cls_names = [7]
# запись файла на диск
img_save_counter = 0
# отслеживание айди объекта
track_id_old = None

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #загрузка модели
    model = get_yolo_track()

    # Open the video file
    source = "C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\in\\cvtest.avi"
    cap = cv2.VideoCapture(source)

    # новый объект лучшего объекта для данного трек_ид
    best_obj = deteceted_object(None, None, None, None)

    # пропуск кадров
    while cap.isOpened():
        if frame_counter % PROCESS_EVERY_N_FRAME != 3:
            cap.grab()
            frame_counter += 1
            continue

        # Read a frame from the video
        success, frame = cap.read()
        frame_counter += 1

        if success:
            # Run YOLO inference on the frame
            # preds = model.predict(source = frame, conf = 0.6, max_det = 5, classes = cls_names, verbose = True)
            preds = model.track(source=frame,
                                conf=0.8,
                                max_det=5,
                                classes=cls_names,
                                verbose=True,
                                tracker="bytetrack.yaml",
                                persist=True,
                                project="Bounding_box",
                                name="center_of_bb")

            for result in preds:
                # Visualize the results on the frame
                annotated_frame = result.plot()
                # рисую линию на прогонзе по которой отслеживаю, что центр объекта подъехал к шлагбауму
                annotated_frame = cv2.line(annotated_frame, line_dot1,
                                           line_dot2, line_color, line_thickness)
                # получаем центр предсказания
                x_center, y_center = bb_center_xy(preds)
                # если объект в нужной области, то
                if y_center > zone_limit_y and x_center > zone_limit_x:

                    # получаем трек_ид его
                    track_id = get_obj_trackId(preds)
                    # и берем первое предсказание
                    curr_obj = deteceted_object(result[0], track_id,
                                                result[0].summary()[0].get('confidence'), annotated_frame)

                    # print("track old = ", track_id_old, " . Track new = ", track_id)
                    # если получаем первый кадр, т.е. такого трек_ид не было еще
                    if track_id_old is None:
                        # print("1. track old is None = ", track_id_old)
                        # то присваиваем ему текущий айдишник
                        track_id_old = track_id

                        # print("bo0 = ")
                        # best_obj.to_string()
                        #сохраняем из списка резалта лучший обнаруженный объект
                        best_obj = deteceted_object(result[0], track_id,
                                                    result[0].summary()[0].get('confidence'), annotated_frame)
                        print("bo1 = ")
                        best_obj.to_string()

                        # сравнивая его с остальными объектами в списке по уверенности
                        for obj in result:
                            if obj.summary()[0].get('confidence') > best_obj.get_conf():
                                best_obj = deteceted_object(obj, track_id,
                                                            obj.summary()[0].get('confidence'), annotated_frame)
                                # print("bo2 = ")
                                # best_obj.to_string()

                        # print("1. track old new val = ", track_id_old)

                    # если у прогнозов одинаковый трек айди, то они сравниваются между собой
                    # оставляя прогноз, у которого больше уверенность
                    elif track_id_old == track_id:
                        # print("new obj, img_save_counter = ", img_save_counter,
                        #       "track old = ", track_id_old, "track id = ", track_id)
                        # for obj in result:
                        #     print(obj.summary())
                        # print("bo3 = ")
                        # best_obj.to_string()

                        for obj in result:
                            # print("bo4 conf = ", best_obj.get_conf())
                            # print("comp with =", obj.summary()[0].get('confidence'))

                            if obj.summary()[0].get('confidence') > best_obj.get_conf():
                                # print("bo5 = TRUE !")
                                best_obj = deteceted_object(obj, track_id,
                                                            obj.summary()[0].get('confidence'), annotated_frame)
                                # print("bo6 = ")
                                # best_obj.to_string()

                    # когда перебраны все объекты по трек айди - то сохраняем лучший на диск
                    elif track_id_old is not None and track_id_old != track_id:
                        # print("3. track old is = ", track_id_old, "track new = ", track_id)
                        # print("Saved obj conf is = ", best_obj.get_conf())

                        # запись объекта на диск
                        x1, y1, x2, y2 = best_obj.get_bb_coors()
                        img_save_counter = img_save(best_obj.get_frame(), x1, y1, x2, y2,
                                                    img_save_counter, best_obj.get_track_id())
                        img_save_counter = img_save_counter + 1

                        # а объект с новым трекером сохраняем для дальнейшего сравнения объекта
                        best_obj = deteceted_object(result[0], track_id,
                                                    result[0].summary()[0].get('confidence'), annotated_frame)
                        # сравниваем с другими объектами предсказания, берем с макс уверенностью
                        for obj in result:
                            if obj.summary()[0].get('confidence') > best_obj.get_conf():
                                best_obj = deteceted_object(obj, track_id,
                                                            obj.summary()[0].get('confidence'), annotated_frame)
                                # print("bo2 = ")
                                # best_obj.to_string()

                        track_id_old = track_id
                        #Модно после распознавания номеров доабвить првоерку на распознанные - чтобы не совпадали

                    desciption(preds)

                    # img_save_counter = img_save(annotated_frame,x1,y1,x2,y2,img_save_counter, track_id)

            #         Display the annotated frame
            #         cv2.imshow("YOLO Inference", annotated_frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            # Break the loop if the end of the video is reached
            break

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()
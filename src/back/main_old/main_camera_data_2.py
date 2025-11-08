import cv2

from src.model import get_yolo_track
from src.image import img_save_bb, print_line_cam1
from src.prediction import bb_center_xy, desciption, get_obj_trackId
from src.deteceted_object import deteceted_object

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
    # загрузка модели
    model = get_yolo_track()

    # Open the video file
    source = "C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\CameraData\\service_zone_in_2.mp4"
    cap = cv2.VideoCapture(source)

    # новый объект лучшего объекта для данного трек_ид
    best_obj = deteceted_object(None, None, None, None)

    # пропуск кадров
    while cap.isOpened():
        if frame_counter % PROCESS_EVERY_N_FRAME != 0:
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
                                max_det=3,
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
                # height, width, channels = annotated_frame.shape
                # print(height, width)
                cv2.imshow("YOLO Inference", image.print_line(annotated_frame))

                cv2.imshow("YOLO Inference", annotated_frame)
                # получаем центр предсказания
                x_center, y_center = bb_center_xy(preds)
                # cv2.imshow("YOLO Inference", image.print_line_in(annotated_frame))

                print("x_c = ", x_center, ". y_c = ", y_center, ". Lim_y = ", zone_limit_in_y, "Lim_X = ", zone_limit_in_x)

                # если объект в нужной области, то
                if y_center > 62 and x_center > 300:
                    print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - -- - - - - - - -")

                    # получаем трек_ид его
                    track_id = get_obj_trackId(preds)
                    # и берем первое предсказание
                    curr_obj = deteceted_object(result[0], track_id,
                                                result[0].summary()[0].get('confidence'), annotated_frame)

                    # если получаем первый кадр, т.е. такого трек_ид не было еще
                    if track_id_old is None:
                        # то присваиваем ему текущий айдишник
                        track_id_old = track_id

                        # сохраняем из списка резалта лучший обнаруженный объект
                        best_obj = deteceted_object(result[0], track_id,
                                                    result[0].summary()[0].get('confidence'), annotated_frame)

                        # сравнивая его с остальными объектами в списке по уверенности
                        for obj in result:
                            if obj.summary()[0].get('confidence') > best_obj.get_conf():
                                best_obj = deteceted_object(obj, track_id,
                                                            obj.summary()[0].get('confidence'), annotated_frame)

                    # если у прогнозов одинаковый трек айди, то они сравниваются между собой
                    # оставляя прогноз, у которого больше уверенность
                    elif track_id_old == track_id:
                        result.save_crop("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\outs\\preds\\",
                                         "_" + str(track_id) + "_obj_" + str(img_save_counter) + ".png")
                        x1, y1, x2, y2 = best_obj.get_bb_coors()
                        img_save_counter = img_save_bb(best_obj.get_frame(), x1, y1, x2, y2,
                                                       img_save_counter, best_obj.get_track_id())
                        img_save_counter = img_save_counter + 1

                        for obj in result:
                            if obj.summary()[0].get('confidence') > best_obj.get_conf():
                                best_obj = deteceted_object(obj, track_id,
                                                            obj.summary()[0].get('confidence'), annotated_frame)

                    # когда перебраны все объекты по трек айди - то сохраняем лучший на диск
                    elif track_id_old is not None and track_id_old != track_id:

                        # запись объекта на диск
                        x1, y1, x2, y2 = best_obj.get_bb_coors()
                        img_save_counter = img_save_bb(best_obj.get_frame(), x1, y1, x2, y2,
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

                        track_id_old = track_id
                        # Можно после распознавания номеров добабвить првоерку на распознанные - чтобы не совпадали

                    desciption(preds)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            if track_id_old != None:
                x1, y1, x2, y2 = best_obj.get_bb_coors()
                img_save_counter = img_save_bb(best_obj.get_frame(), x1, y1, x2, y2,
                                               img_save_counter, best_obj.get_track_id())
                img_save_counter = img_save_counter + 1
            # Break the loop if the end of the video is reached
            break

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()

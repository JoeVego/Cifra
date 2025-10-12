import cv2

from src.model import get_yolo_track_by_path
from src.image import img_save_bb, print_line_cam1
from src.prediction import bb_center_xy
from src.deteceted_object import deteceted_object

# пропуск кадров
PROCESS_EVERY_N_FRAME = 2
# счетчик кадров
frame_counter = 0
# запись файла на диск
img_save_counter = 0
# отслеживание айди объекта
track_id_old = None
# weights_path
weights_path = "data/weights/0810_lp_ds_learn_yolo11_best.pt"
# In data video file path
source = "C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\cam_full_vid\\test.mp4"

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # загрузка модели
    model = get_yolo_track_by_path(weights_path)

    # Open the video file
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
                                conf=0.3,
                                max_det=3,
                                verbose=True,
                                persist=True)

            for results in preds:
                # Visualize the results on the frame
                annotated_frame = results.plot()

                # рисую линию на прогонзе по которой отслеживаю, что центр объекта подъехал к шлагбауму
                cv2.imshow("YOLO Inference", print_line_cam1(annotated_frame))

                for result in results:
                # получаем центр предсказания
                    x_center, y_center = bb_center_xy(result)
                    print(result.summary()[0].get('track_id'))

                    if y_center > 120:
                        # получаем трек_ид его
                        track_id = result.summary()[0].get('track_id')

                        # если получаем первый кадр, т.е. такого трек_ид не было еще
                        if track_id_old is None:
                            # то присваиваем ему текущий айдишник
                            track_id_old = track_id

                            # сохраняем из списка резалта первый обнаруженный объект
                            if best_obj.get_track_id() is None:
                                best_obj = deteceted_object(result, track_id,
                                                            result.summary()[0].get('confidence'), annotated_frame)

                            # result.save_crop("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\outs\\yolo_lp_4\\",
                            #                  "_" + str(track_id) + "_obj_" + str(img_save_counter) + ".png")

                        # если у прогнозов одинаковый трек айди, то они сравниваются между собой
                        # оставляя прогноз, у которого больше уверенность
                        elif track_id_old == track_id:

                            if  result.summary()[0].get('confidence') > best_obj.get_conf():
                                best_obj = deteceted_object(result, track_id,
                                                            result.summary()[0].get('confidence'), annotated_frame)

                            # result.save_crop("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\outs\\yolo_lp_4\\",
                            #                  "_" + str(track_id) + "_obj_" + str(img_save_counter) + ".png")

                        # когда перебраны все объекты по трек айди - то сохраняем лучший на диск
                        elif track_id_old != track_id:
                            print("bbox shape = ", annotated_frame.shape)
                            print("orig shape = ", frame.shape)

                            # запись объекта на диск
                            result.save_crop("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\outs\\yolo_lp_4\\",
                                             "_" + str(track_id) + "_obj_" + str(img_save_counter) + ".png")
                            img_save_counter = img_save_counter + 1

                            # а объект с новым трекером сохраняем для дальнейшего сравнения объекта
                            best_obj = deteceted_object(result, track_id,
                                                        result.summary()[0].get('confidence'), annotated_frame)

                            track_id_old = track_id

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()

from ultralytics import YOLO
import cv2

from model import get_yolo_track
from image import line_dot1, line_dot2, line_color, line_thickness
from image import zone_limit_x, zone_limit_y, img_save
from prediction import bb_center_xy, desciption, get_id_coords, get_obj_trackId

# пропуск кадров
PROCESS_EVERY_N_FRAME = 5
# счетчик кадров
frame_counter = 0
# ищем только класс грузовики = 7
cls_names = [7]
# запись файла на диск
img_save_counter = 0
# айди объекта
track_id_old = -1

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    model = get_yolo_track()

    # Open the video file
    source = "C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\in\\cvtest.avi"
    cap = cv2.VideoCapture(source)

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
            # preds = model(frame)
            # preds = model.predict(source = frame, conf = 0.6, max_det = 5, classes = cls_names, verbose = True)
            preds = model.track(source=frame,
                                conf=0.7,
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
                # рисую линию по которой отслеэиваю, что центр объекта подъехал к шлагбауму
                annotated_frame = cv2.line(annotated_frame, line_dot1,
                                           line_dot2, line_color, line_thickness)
                # получаем центр предсказания
                x_center, y_center = bb_center_xy(preds)
                # если объект в нужной области, то
                if y_center > zone_limit_y and x_center > zone_limit_x:
                    # для проверки кода
                    # annotated_frame = cv2.putText(annotated_frame, "CHECK", bottomLeftCornerOfText,
                    #   text_font, fontScale, fontColor, thickness, lineType)

                    # текстовое описание найденного объекта
                    # desciption(preds)

                    # работа с трек айди
                    track_id = get_obj_trackId(preds)
                    if track_id_old == -1:
                        track_id_old = track_id
                    if track_id_old != track_id:
                        print("new obj, img_save_counter = ", img_save_counter,
                              "track old = ", track_id_old, "track id = ", track_id)
                        track_id_old = track_id
                        # 2. обрабабоать None значения айдишника
                        # 3. сохранять лишь изображения с найвысшей уверенностью
                        # оставляють с лучшей уверенностью фото

                    desciption(preds)

                    x1, y1, x2, y2 = get_id_coords(preds)
                    img_save_counter = img_save(annotated_frame, x1, y1, x2, y2,
                                                img_save_counter, track_id)
                    img_save_counter = img_save_counter + 1

            #         Display the annotated frame
            #         cv2.imshow("YOLO Inference", annotated_frame)

            #          Если вывод нужен на каждый кадр - включить
            #         desciption(preds)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            # Break the loop if the end of the video is reached
            break

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()
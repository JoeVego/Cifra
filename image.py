import cv2

line_dot1 = (1000, 580)
line_dot2 = (1600, 610)
line_color = (255, 255, 255)
line_thickness = 10

zone_limit_x = 800
zone_limit_y = 510

text_font = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (30, 30)
fontScale = 1
fontColor = (255, 255, 255)
thickness = 2
lineType = 2


def img_save(car_img, x1, y1, x2, y2, counter_img, track_id):
    crop_img = car_img[y1:y2, x1:x2]
    cv2.imshow("YOLO Inference", crop_img)

    filename = ("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\outs\\preds\\"
                + str(track_id) + "_obj_" + str(counter_img) + ".png")

    cv2.imwrite(filename, crop_img)

    return counter_img

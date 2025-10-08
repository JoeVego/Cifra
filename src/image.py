import cv2

line_dot1 = (600, 95)
line_dot2 = (50, 95)
line_dot3 = (600, 95)
line_dot4 = (600, 464)
line_color = (255, 0, 255)
line_thickness = 5

zone_limit_x = 600
zone_limit_y = 80

zone_limit_in_x = 300
zone_limit_in_y = 50

text_font = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (30, 30)
fontScale = 1
fontColor = (255, 255, 255)
thickness = 2
lineType = 2


def img_save(car_img, x1, y1, x2, y2, counter_img, track_id):
    crop_img = car_img[y1:y2, x1:x2+10]
    # cv2.imshow("YOLO Inference", crop_img)

    filename = ("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\outs\\yolo_license_plate_3"
                + str(track_id) + "_obj_" + str(counter_img) + ".png")

    cv2.imwrite(filename, crop_img)

    return counter_img


def print_line(frame):
    frame = cv2.line(frame, line_dot3, line_dot4, line_color, line_thickness)
    # return frame
    return cv2.line(frame, line_dot1, line_dot2, line_color, line_thickness)

def print_line_in(frame):
    line_dot_in_1 = (500, 0)
    line_dot_in_2 = (500, 75)
    line_dot_in_3 = (500, 75)
    line_dot_in_4 = (800, 75)
    line_color = (255, 0, 255)
    line_thickness = 5

    frame = cv2.line(frame, line_dot_in_3, line_dot_in_4, line_color, line_thickness)
    return cv2.line(frame, line_dot_in_1, line_dot_in_2, line_color, line_thickness)
import cv2

line_dot1 = (600, 95)
line_dot2 = (50, 95)
line_dot3 = (600, 95)
line_dot4 = (600, 464)
line_color = (255, 0, 255)
line_thickness = 5

text_font = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (30, 30)
fontScale = 1
fontColor = (255, 255, 255)
thickness = 2
lineType = 2


def img_save_bb(car_img, x1, y1, x2, y2, counter_img, track_id):
    crop_img = car_img[y1:y2, x1:x2]

    filename = ("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\outs\\yolo_lp_4\\"
                + str(track_id) + "_obj_" + str(counter_img) + ".png")

    cv2.imwrite(filename, crop_img)

    return counter_img

def print_line(frame):
    frame = cv2.line(frame, line_dot3, line_dot4, line_color, line_thickness)
    # return frame
    return cv2.line(frame, line_dot1, line_dot2, line_color, line_thickness)

def print_line_cam1(frame):
    line_dot_in_3 = (0, 280)
    line_dot_in_4 = (1350, 280)
    line_dot_in_1 = (250, 280)
    line_dot_in_2 = (250, 1080)

    line_color = (255, 0, 255)
    line_thickness = 5
    img_temp = cv2.line(frame, line_dot_in_1, line_dot_in_2, line_color, line_thickness)

    return cv2.line(img_temp, line_dot_in_3, line_dot_in_4, line_color, line_thickness)
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

def print_line(frame):
    frame = cv2.line(frame, line_dot3, line_dot4, line_color, line_thickness)
    # return frame
    return cv2.line(frame, line_dot1, line_dot2, line_color, line_thickness)

def get_bb_coords_by_result(result):
    margin = 66

    xyxy = result.boxes.xyxy
    top_left_x = int(xyxy[0][0].item())
    top_left_y = int(xyxy[0][1].item())
    bottom_right_x = int(xyxy[0][2].item())
    bottom_right_y = int(xyxy[0][3].item())
    return top_left_x - margin, top_left_y - margin, bottom_right_x + margin, bottom_right_y + margin

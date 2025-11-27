def desciption(predictions):
    for obj in predictions:
        print(obj.summary())
        #          подробный формат вывода
        #         print(obj.verbose())
        print("- - - - - -")


# Получение центра ограничивающей рамки
def bb_center_xy(result):
    bb_tensor = result.boxes.xyxy

    x1 = round(bb_tensor.tolist()[0][0])
    y1 = round(bb_tensor.tolist()[0][1])
    x2 = round(bb_tensor.tolist()[0][2])
    y2 = round(bb_tensor.tolist()[0][3])

    xc = (x1 + x2) // 2
    yc = (y1 + y2) // 2

    # print("For x1= ",x1 , " x2= ",x2 , " and y1= ",y1 , " y2= ",y2 , " . Center is xc= ",xc , " yc=",yc)
    return xc, yc


def bb_center_by_res(result):
    for obj in result:
        bb_tensor = obj.boxes.xyxy

        x1 = round(bb_tensor.tolist()[0][0])
        y1 = round(bb_tensor.tolist()[0][1])
        x2 = round(bb_tensor.tolist()[0][2])
        y2 = round(bb_tensor.tolist()[0][3])

        xc = (x1 + x2) // 2
        yc = (y1 + y2) // 2

    # print("For x1= ",x1 , " x2= ",x2 , " and y1= ",y1 , " y2= ",y2 , " . Center is xc= ",xc , " yc=",yc)
    return xc, yc


# Получение координат ограничивающей рамки
def get_id_coords(preds):
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0

    for obj_list in preds:
        for obj in obj_list:
            bb_tensor = obj.boxes.xyxy

            x1 = round(bb_tensor.tolist()[0][0])
            y1 = round(bb_tensor.tolist()[0][1])
            x2 = round(bb_tensor.tolist()[0][2])
            y2 = round(bb_tensor.tolist()[0][3])

    # print("For x1= ",x1 , " x2= ",x2 , " and y1= ",y1 , " y2= ",y2)
    return x1, y1, x2, y2


# Получение трек айди объекта
def get_obj_trackId(results):
    # for obj in preds:
    return results.summary()[0].get('track_id')

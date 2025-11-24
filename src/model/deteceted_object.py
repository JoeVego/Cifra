class deteceted_object:
    def __init__(self, result_obj, track_id, conf, frame):
        self.result_obj = result_obj
        self.track_id = track_id
        self.conf = conf
        self.frame = frame

    def get_track_id(self):
        return self.track_id

    def get_result_obj(self):
        return self.result_obj

    def get_conf(self):
        return self.conf

    def get_frame(self):
        return self.frame

    def get_bb_coors(self):
        bb_tensor = self.result_obj.boxes.xyxy

        x1 = round(bb_tensor.tolist()[0][0])
        y1 = round(bb_tensor.tolist()[0][1])
        x2 = round(bb_tensor.tolist()[0][2])
        y2 = round(bb_tensor.tolist()[0][3])

        # print("For x1= ",x1 , " x2= ",x2 , " and y1= ",y1 , " y2= ",y2)
        return x1, y1, x2, y2

    def to_string(self):
        print("- Object - ")
        print("Res_obj: ", self.result_obj)
        print("id: ", self.track_id)
        print("conf: ", self.conf)
        print("- Object - ")

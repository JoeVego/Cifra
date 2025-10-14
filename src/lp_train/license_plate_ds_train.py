from ultralytics import YOLO
import cv2

#ds = https://universe.roboflow.com/ru-anrp/russian-license-plates-detector/dataset/3


#Обучение
# if __name__ == '__main__':
#     print(os.listdir("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\data_rf\\train"))
#
#     model = YOLO("yolo11n.pt")
#
#     result = model.train(
#         data="C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\data_rf\\data.yaml",
#         epochs=2,
#         batch=4,
#         # imgsz= 640,
#         project="C:\\Users\\Admin\\Desktop\\Study\\Cifra\\runs")


# Применение
if __name__ == '__main__':
    model = YOLO("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\weights\\best.pt")

    # Define current screenshot as source
    source = "C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\outs\\preds_2\\self.jpg"

    # Run inference on the source
    results = model(source)  # list of Results objects

    for result in results:
        # Visualize the results on the frame
        annotated_frame = result.plot()
        cv2.imshow("YOLO Inference", annotated_frame)

        filename = ("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\outs\\preds\\"
                    + str(6) + "_obj_" + str(9) + ".png")

        cv2.imwrite(filename, annotated_frame)
from ultralytics import YOLO

import os
import torch
import numpy as np
import pandas as pd

from tqdm.auto import tqdm
import shutil as sh

import matplotlib.pyplot as plt
from IPython.display import Image, clear_output

#ds = https://universe.roboflow.com/ru-anrp/russian-license-plates-detector/dataset/3

if __name__ == '__main__':
    print(os.listdir("C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\data_rf\\train"))

    model = YOLO("yolo11n.pt")

    result = model.train(
        data="C:\\Users\\Admin\\Desktop\\Study\\Cifra\\data\\data_rf\\data.yaml",
        epochs=2,
        batch=4,
        # imgsz= 640,
        project="C:\\Users\\Admin\\Desktop\\Study\\Cifra\\runs")
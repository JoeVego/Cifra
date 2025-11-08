import os

if __name__ == '__main__':
    # создать новый текстовый файл
    text_file = open("labels2.csv", "w")
    # запить текста в этот файл
    text_file.write("filename,words")

    path = "/data/NomeroffNet/NomeroffNetDs/autoriaNumberplateOcrRu-2021-09-01/val/img_3\\"

    for filename in os.listdir(path):
        # text_file.write()

        filename = filename[:-4]
        if filename[-2] == "_":
            filename_ocr = filename[:-2]
        else:
            filename_ocr = filename
        # print("edited = ", filename)

        str = "\n" + filename + ".png," + filename_ocr
        text_file.write(str)

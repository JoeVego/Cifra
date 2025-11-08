import easyocr

if __name__ == '__main__':
    # reader = easyocr.Reader(['ru']) # this needs to run only once to load the model into memory
    path = "C:/Users/Admin/Desktop/Study/Cifra/data/outs/api_lp_5/license-plate/_None_obj_13_conf_0.34905.jpg"
    # result = reader.readtext(path, allowlist='АВЕКМНОРСТУХ0123456789')

    reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory
    # result = reader.readtext(path, allowlist='ABEKMHOPCTYX0123456789')
    result = reader.readtext(path, allowlist='ABCEHKMOPTYX0123456789')

    # отедльно серию и номер ??? обучить моедль ?
    print(result)
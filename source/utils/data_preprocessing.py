import os
import csv
from configs.load_config import LoadConfig

APP_CFG = LoadConfig()

def csv2txt(csv_link):
    data_text = ''
    with open(csv_link, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Lấy thông tin từ mỗi hàng của file CSV
            PRODUCT_NAME = row['PRODUCT_NAME']  # Thay 'Tên Sản Phẩm' bằng tên cột chứa tên sản phẩm trong file CSV của bạn
            PRODUCT_INFO_ID = row['PRODUCT_INFO_ID']  # Thay 'ID' bằng tên cột chứa ID sản phẩm trong file CSV của bạn
            PRODUCT_CODE = row['PRODUCT_CODE']  # Thay 'Code' bằng tên cột chứa mã code sản phẩm trong file CSV của bạn
            SPECIFICATION_BACKUP = row['SPECIFICATION_BACKUP']
            QUANTITY_SOLD = row['QUANTITY_SOLD']
            RAW_PRICE = row['RAW_PRICE']
            # In ra văn bản theo định dạng mong muốn
            s = f"Sản phẩm: {PRODUCT_NAME} có ID là: {PRODUCT_INFO_ID}, mã sản phẩm(mã Code) là: {PRODUCT_CODE}, thông tin chi tiết về sản phẩm: {PRODUCT_NAME}: {SPECIFICATION_BACKUP}, số lượng: {PRODUCT_NAME} đã bán là: {QUANTITY_SOLD}, sản phẩm: {PRODUCT_NAME} có giá:{RAW_PRICE}\n"
            data_text = data_text + s
            # print(s)
    return data_text


def convert_csv_to_txt():
    directory_txt = APP_CFG.text_product_directory
    directory_csv = APP_CFG.csv_product_directory

    files = [f for f in os.listdir(directory_csv) if os.path.isfile(os.path.join(directory_csv, f))]
    csv_files = [f for f in files if f.endswith('.csv')]

    for csv_file in csv_files:
        # Đọc file CSV
        csv_path = os.path.join(directory_csv, csv_file)
        txt_file = csv_file.replace('.csv', '.txt')
        txt_path = os.path.join(directory_txt, txt_file)
        data_text = csv2txt(csv_path)
        with open(txt_path, "w", encoding='utf-8') as file:
            file.write(data_text)
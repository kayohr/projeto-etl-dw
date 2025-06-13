from src.extract.extract_api import extract_data
from src.transform.transform_data import transform_data
from src.load.load_dw import load_dw

if __name__ == '__main__':
    extract_data()
    transform_data()
    load_dw()

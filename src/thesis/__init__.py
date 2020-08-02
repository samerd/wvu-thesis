'''
Author: Samir deeb
'''
import os


def get_dataset_dir():
    curr_dir = os.path.dirname(__file__)
    data_dir = os.path.join(curr_dir, os.pardir, os.pardir, "dataset")
    data_dir = os.path.normpath(data_dir)
    return data_dir

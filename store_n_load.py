import os.path
import pickle


'''
module to store/load python objects in/from text file
'''


def store(pyobject, file_name, save_path):
    complete_name = os.path.join(save_path, file_name + '.txt')
    file = open(complete_name, "wb")
    pickle.dump(pyobject, file)
    file.close()


def load(file_name, save_path):
    complete_name = os.path.join(save_path, file_name + '.txt')
    file = open(complete_name, "rb")
    return pickle.load(file)


def store_csv(pyobject, file_name, save_path):
    complete_name = os.path.join(save_path, file_name + '.csv')
    file = open(complete_name, "wb")
    pickle.dump(pyobject, file)
    file.close()


def load_csv(file_name, save_path):
    complete_name = os.path.join(save_path, file_name + '.csv')
    file = open(complete_name, "rb")
    return pickle.load(file)

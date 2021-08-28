from os import path, listdir
from getpass import getuser
from shutil import copy
from PIL import Image
from time import ctime

destination_folder = r'C:\Users\mkali\Pictures\Background Images' #input('Paste here the path for the images destination folder: ')#

active_user = getuser()

source_folder = r'C:\Users\%s\AppData\Local\Packages\Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy\LocalState\Assets' %active_user

for file_name in listdir(source_folder):
    full_file_name = path.join(source_folder, file_name)
    if Image.open(full_file_name).size[0] > 1500:
        copy(full_file_name, path.join(destination_folder, file_name + '.png'))
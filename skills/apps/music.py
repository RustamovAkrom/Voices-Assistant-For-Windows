import os
import random


def open_music():
    path_to_dir_songs = "D:\Songs" # Replace to your directory
    list_path_to_dir_songs = os.listdir(path_to_dir_songs)
    count_path_to_dir_songs = len(list_path_to_dir_songs)
    random_music_file_from_dir = list_path_to_dir_songs[
        random.randint(0, count_path_to_dir_songs)
    ]
    random_music = f"{path_to_dir_songs}\{random_music_file_from_dir}"
    os.startfile(random_music)


def close_music():
    os.system("taskkill /f /im MediaPlayer.exe")

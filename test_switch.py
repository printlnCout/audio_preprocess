#author: lei_chang
#data: 2019/8/3
#successful playform: win10
#web: help.nchsoftware.com/help/en/switch/win/switchcommandlinetool.html

import os
import subprocess
import time
from pydub import AudioSegment
import pandas as pd
import random
import librosa
import numpy as np

config={
    'switch_exe_path': 'C:\\"Program Files"\\"NCH Software"\\Switch\\switch.exe',
    'input_folder': 'C:\\Users\\lei\\Downloads\\music\\',
    'output_folder': 'C:\\Users\\lei\\Downloads\\change_music\\',
    'temp_folder': 'C:\\Users\\lei\\Downloads\\temp_folder\\',
    'input_settings': '.vox'+' '+'0'+' '+'6000'+' '+'1', #audio_type+codec_type+sample_size+channels_number
    'output_settings':  '.wav'+' '+'PCM8'+' '+'6000'+' '+'1', #audio_type+codec_type+sample_size+channels_number
    'overwrite_type': 'ALWAYS',

    'error_audio_path': 'C:\\Users\\lei\\Downloads\\temp_folder\\error_audio_list.txt',
    'other_audio_path': 'C:\\Users\\lei\\Downloads\\temp_folder\\other_audio_path.txt',
    'not_change_right_list': 'C:\\Users\\lei\\Downloads\\temp_folder\\not_change_right_list.txt',
    'min_duration_filter': 0,

    'slice_final_15s_folder': 'C:\\Users\\lei\\Downloads\\slice_final_15s_folder\\',
    'file_type': 'wav',

    'split_slice_or_not': True,
    #'MAX_SONGS_PER_CLASS': 5000,
    'ROOT_ID_BEGIN': 200000000,
    #'split_duration': 50,
    'one_split_duration': 4,
    'min_duration_filter': 4,
    'file_type': 'wav',
    'DATA_IN_PUT_PATH': "/home/lei_chang/dianxin_pt_yy/temp_data/audio_200_not_change/", #"/home/lei_chang/dianxin_pt_yy/temp_data/audio_200/",
    'temp_slice_song_dir': "/home/lei_chang/dianxin_pt_yy/temp_data/temp_slice_song_dir/",
    #'SLICES_OUT_PUT_PATH': '/home/lei_chang/dianxin_pt_yy/temp_data/mel_pt_yy_2000_part/dianxin_slices_4S_1024fft_32hop_128mel/', #"/home/gyx/mel/scene_slices_5S_1024fft_512hop_128mel/",
    #'DATA_CSV_OUT_PUT_PATH': r'/home/lei_chang/dianxin_pt_yy/temp_data/scene_pt_yy_2000_part/dianxin_slices_4S_1024fft_32hop_128mel_song.csv',
    #'SLICES_CSV_OUT_PUT_PATH': r'/home/lei_chang/dianxin_pt_yy/temp_data/scene_pt_yy_2000_part/dianxin_slices_4S_1024fft_32hop_128mel_slice.csv',
    'SAMPLE_RATE': 6000,
    'hop': 32,
    'n_fft': 1024,
    'n_mels': 128,
    'clips_per_song': 7,
    'melspec_OUT_PUT_ROOT': "/home/lei_chang/dianxin_pt_yy/temp_data/mel_pt_yy_2000_part/dianxin_slices_4S_1024fft_32hop_128mel_spectrogram/",
    'CSV_OUT_PUT_PATH': r'/home/lei_chang/dianxin_pt_yy/temp_data/scene_pt_yy_2000_part/dianxin_slices_4S_1024fft_32hop_128mel_spectrogram.csv'

}

def run_command_line():
    # hold on, not transform......
    #os.system('C:\\"Program Files"\\"NCH Software"\\Switch\\switch.exe -hide -convert -addfolder "C:\\Users\\lei\\Downloads\\music" -outfolder "C:\\Users\\lei\\Downloads\\change_music" -format .wav -settings .wav PCM16 8000 1')#

    # successfully, if you use this, first open the software, then choose the initial "set codecsettings individually" for coverting from ".raw/.vox"
    #os.system('C:\\"Program Files"\\"NCH Software"\\Switch\\switch.exe  -hide -convert  -addfolder "C:\\Users\\lei\\Downloads\\music" -outfolder "C:\\Users\\lei\\Downloads\\change_music"  -settempfolder "C:\\Users\\lei\\Downloads\\temp_folder" -insettings .vox 0 6000 1 -settings .wav PCM8 6000 1 -overwrite ALWAYS')

    # using string function '+' in python, just as the second way
    command_line_change = config['switch_exe_path'] + '  -hide'+' -convert'+'  -addfolder '+config['input_folder']+' -outfolder '+config['output_folder']+' -settempfolder '+config['temp_folder']+' -insettings '+config['input_settings']+' -settings '+config['output_settings']+' -overwrite '+config['overwrite_type']
    os.system(command_line_change)

    # this can also use, but also can't clip
    #command_line_change = config['switch_exe_path']+' -convert'+'  -addfolder '+config['input_folder']+' -outfolder '+config['output_folder']+' -settempfolder '+config['temp_folder']+' -insettings '+config['input_settings']+' -settings '+config['output_settings']+' -overwrite '+config['overwrite_type']+' -clear'
    #retcode = subprocess.call(command_line_change, shell=True)

    #command_line_delete = config['switch_exe_path']+' -clear'
    #retcode = subprocess.call(command_line_delete , shell=True)
    #child = subprocess.Popen(command_line_change, shell=True)
    #child.wait()

    #subprocess.call("sh C:\\Users\\lei\\Desktop\\test.sh")
    #subprocess.call("sh C:\\Users\\lei\\Desktop\\second.sh")

def clip_final_15s():
    error_audio_list = []
    changed_audio = os.listdir(config['output_folder'].replace('"', ''))
    for item_audio in changed_audio:
        try:
            song_au = AudioSegment.from_file(config['output_folder'].replace('"', '') + item_audio)
            # print(song_au.duration_seconds)
        except Exception:
            error_audio_list.append(item_audio)
            continue
        if song_au.duration_seconds < config['min_duration_filter']:
            error_audio_list.append(item_audio)
            continue
        if song_au.duration_seconds < 15:
            begin = 0
        else:
            begin = (song_au.duration_seconds - 15) * 1000
        slice_au = song_au[begin:]

        slice_final_15s_folder = config['slice_final_15s_folder'].replace('"', '')
        if not os.path.exists(slice_final_15s_folder):
            os.makedirs(slice_final_15s_folder)

        slice_au.export(slice_final_15s_folder+item_audio, format=config['file_type'])

    if error_audio_list:
        print('========')
        print('error_audio_list')
        print('========')
        with open(config['error_audio_path'].replace('"', ''), 'w') as fw:
            fw.write('\n'.join(error_audio_list))

def check_change_command():
    changed_audio = os.listdir(config['output_folder'].replace('"', ''))
    source_audio = os.listdir(config['input_folder'].replace('"', ''))
    changed_audio = list(map(lambda x: x.replace('.wav', '.VOX'), changed_audio))

    same_list = set(source_audio)&(set(changed_audio))
    print('changed audio numbers: ', len(same_list))
    print('all audio numbers: ', len(source_audio))

    other_audio = list(set(changed_audio).difference(same_list))
    if other_audio:
        print('========')
        print('other_audio')
        print(other_audio)
        print('========')
        with open(config['other_audio_path'].replace('"', ''), 'w') as fw:
            fw.write('\n'.join(other_audio))

    not_change_right_list = list(set(changed_audio).difference(same_list))
    if not_change_right_list:
        print('========')
        print('not_change_right_list')
        print(not_change_right_list)
        print('========')
        with open(config['not_change_right_list'].replace('"', ''), 'w') as fw:
            fw.write('\n'.join(not_change_right_list))

    # check the duration and sample size and channels of audio
    #for item_audio in changed_audio:
    #    song_au = AudioSegment.from_file(config['output_folder'].replace('"', '') + song)

def transfer_slicing():
    transfer_finished = False
    clip_finished = False
    before_change_number = len(os.listdir(config['output_folder']))
    if before_change_number :
        print('=====')
        print('there are some audio')
    print('begin changing: \n')
    run_command_line()

    while transfer_finished == False:
        changed_numbers = len(os.listdir(config['output_folder']))
        if changed_numbers == len(os.listdir(config['input_folder'])):
            transfer_finished = True
        else:
            time.sleep(5)
    print('finish changing: \n')
    os.system(config['switch_exe_path']+' -clear'+ ' -exit')

    print('begin slicing: \n')
    clip_final_15s()

    while clip_finished == False:
        clip_numbers = len(os.listdir(config['slice_final_15s_folder']))
        if clip_numbers == len(os.listdir(config['input_folder'])):
            clip_finished = True
        else:
            time.sleep(5)

    print('finish slicing: \n')

def get_clips(song_au):
    slices = []
    count = 0
    begin = 0
    end = int(song_au.duration_seconds - config['one_split_duration']) * 1000
    while count < config['clips_per_song']:
        start = random.randint(begin, end)
        slices.append(song_au[start: (start + config['one_split_duration'] * 1000)])
        count += 1
    return slices

def clip_and_make_mel():

    slice_id_list = []
    slice_path_list = []
    song_path_list = []
    slice_class_list = []
    melspec_path_list = []
    slice_id_split = []

    error_class_list = []

    # 得到类别
    classes = os.listdir(config['DATA_IN_PUT_PATH'])
    for one_class in classes:
        class_npy_dir = config['melspec_OUT_PUT_ROOT'] + one_class + "/"
        if os.path.exists(class_npy_dir) is False:
            os.makedirs(class_npy_dir)

        if os.path.exists(config['melspec_OUT_PUT_ROOT']) is False:
            os.makedirs(config['melspec_OUT_PUT_ROOT'])

        if os.path.exists(config['temp_slice_song_dir']) is False:
            os.makedirs(config['temp_slice_song_dir'])

        print("开始处理", one_class)
        class_id_root = config['ROOT_ID_BEGIN'] + classes.index(one_class) * (
                config['ROOT_ID_BEGIN'] // 100 // int(str(config['ROOT_ID_BEGIN'])[0]))
        one_class_path = config['DATA_IN_PUT_PATH'] + one_class + '/'
        one_class_relative_path = one_class + '/'
        songs = os.listdir(one_class_path)
        random.shuffle(songs)
        id_temp = 0
        # id_use = 0
        for song in songs:
            original_id = class_id_root + id_temp
            # 切片

            if config['split_slice_or_not']:
                try:
                    song_au = AudioSegment.from_file(one_class_path + song)
                    # print(song_au.duration_seconds)
                except Exception:
                    error_class_list.append(one_class_path + song)
                    id_temp += 1
                    continue
                if song_au.duration_seconds < config['min_duration_filter']:
                    id_temp += 1
                    continue
                # midpoint = song_au.duration_seconds // 2
                # left_four_seconds = (midpoint - config['split_duration'] // 2) * 1000  # pydub workds in milliseconds
                # right_four_seconds = (midpoint + config['split_duration'] // 2) * 1000  # pydub workds in milliseconds
                # middle = song_au[left_four_seconds:right_four_seconds]
                # slices = middle[::config['one_split_duration'] * 1000]
                # slices = song_au[::config['one_split_duration'] * 1000]

                slices = get_clips(song_au)

                i = 0
                for slice in slices:
                    print("处理第" + str(original_id) + "歌曲的第" + str(i) + "个")
                    slice_name = str(original_id) + '#' + str(i) + '.' + config['file_type']
                    slice_id = str(original_id) + '#' + str(i)

                    slice.export(config['temp_slice_song_dir'] + slice_name,
                                 format=config['file_type'])
                    audio, sr = librosa.load(config['temp_slice_song_dir'] + slice_name, sr=config['SAMPLE_RATE'], mono=True)
                    os.remove(config['temp_slice_song_dir'] + slice_name)

                    # 如果文件夹不存在则创建文件夹
                    spec = librosa.feature.melspectrogram(y=audio, sr=config['SAMPLE_RATE'], hop_length=config['hop'],
                                                          n_fft=config['n_fft'], n_mels=config['n_mels'])
                    # 如果文件夹不存在则创建文件夹
                    #temp_dir = config['melspec_OUT_PUT_ROOT'] + one_class + "/"
                    #if os.path.exists(temp_dir) is False:
                    #    os.makedirs(temp_dir)
                    spec_original_path = one_class + '/' + slice_id
                    # 转置
                    np.save(config['melspec_OUT_PUT_ROOT'] + spec_original_path, spec)

                    slice_id_list.append(slice_id)
                    melspec_path_list.append(spec_original_path + '.npy')
                    slice_class_list.append(one_class)
                    song_path_list.append(config['DATA_IN_PUT_PATH']+one_class+'/'+song)
                    slice_path_list.append(one_class_relative_path + slice_name)
                    slice_id_split.append(slice_id.split('#')[0])

                    i += 1
                    print(slice_id)

            id_temp += 1
            # id_use += 1
            # if id_use > config['MAX_SONGS_PER_CLASS']:
            #    break
        print("目前错误的歌曲数量", len(error_class_list))

    data2 = {
        'id': slice_id_list,
        'path': melspec_path_list,
        #'slice_path_list': slice_path_list,
        'class': slice_class_list,
        'song_path': song_path_list,
        'id_split': slice_id_split
    }
    csv_df3 = pd.DataFrame(data2, columns=['id', 'path', 'class', 'song_path', 'id_split'])
    csv_df3.to_csv(config['CSV_OUT_PUT_PATH'], index=False, encoding='utf')

def check_make_mel():
    csv_mel_file = pd.read_csv(config['CSV_OUT_PUT_PATH'])
    csv_count = csv_mel_file.groupby(['id_split']).count()
    npy_clip_count = csv_count[csv_count['id'] != config['clips_per_song']]

    if npy_clip_count.shape[0] != 0:
        print('=============')
        print('the error song name that clip numbers not correct: ')
        print(npy_clip_count.index)

    not_exist_npy_file = []
    for index, row in csv_mel_file.iterrows():
        clip_npy_path = config['melspec_OUT_PUT_ROOT'] + row['path']
        if not os.path.exists(clip_npy_path):
            not_exist_npy_file.append(row['id'])

    if len(not_exist_npy_file) != 0:
        print('==============')
        print('not_exist_npy_file: ')
        print(not_exist_npy_file)

    return npy_clip_count, not_exist_npy_file

if __name__ == '__main__':
    transfer_slicing()
    check_change_command()

    clip_and_make_mel()
    check_make_mel()
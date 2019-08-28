# this code is copyed from my classmate Zhao Zi Long, modified by lei_chang
# 代码逻辑是先对每帧检测是否是有说话，再检测，当队列(长度10帧)中连续出现9个或以上说话帧时，识别为(说话模式)，直到检测到队列(长度10帧)中连续出现9个或以上非说话帧时，退出(说话模式)，将其间的所有帧 保留为一个切片
# if there is any bug, you can just contact me
# also from web: https://blog.csdn.net/benhuo931115/article/details/54909228
# my mail: 201821038849@mail.scut.edu.cn

import collections
import contextlib
import sys
import os
import wave

import webrtcvad

config = {
    'frame_duration_ms': 30,
    'padding_duration_ms': 300,
    'sensitivity': 3, #vad检测的敏感系数，激进程度与数值大小正相关。0: Normal，1：low Bitrate， 2：Aggressive；3：Very Aggressive
    'audio_path': '/home/lei/音乐/电信原始音频/第三次/20190729/pt_wav_15s/pt_2018082875807636751_副本.wav',
    'buffer_size_thread': 0.9
}

def read_wave(path):
    """Reads a .wav file.
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        #print("sample_rate: ", sample_rate)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    """Writes a .wav file.
    """
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    """Represents a "frame" of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0

    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n

# 在帧级进行静音统计，if is speech , add 1 , else 0
def get_frame_silence_time(frames, vad, sample_rate):
    count_speech_frame = 0
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)
        if is_speech:
            count_speech_frame += 1

    frame_all_time = len(frames) * config['frame_duration_ms']
    frame_remain_time = count_speech_frame * config['frame_duration_ms']
    frame_silence_time = (len(frames) - count_speech_frame) * config['frame_duration_ms']
    print('all time: ', frame_all_time)
    print('remain time: ', frame_remain_time)
    print('remove time: ', frame_silence_time)
    print('==============')
    return frame_all_time, frame_remain_time, frame_silence_time

def vad_collector(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False

    voiced_frames = []

    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)

        sys.stdout.write('1' if is_speech else '0')
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > config['buffer_size_thread'] * ring_buffer.maxlen:
                triggered = True
                sys.stdout.write('+(%s)' % (ring_buffer[0][0].timestamp,))
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if num_unvoiced > config['buffer_size_thread'] * ring_buffer.maxlen:
                sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                triggered = False
                yield (b''.join([f.bytes for f in voiced_frames]), len(voiced_frames))
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
    sys.stdout.write('\n')
    if voiced_frames:
        yield (b''.join([f.bytes for f in voiced_frames]), len(voiced_frames))

# 赵子文将音频切分出几段，在切片级统计这几段总时长，其余时间视为为静音时间
def get_clip_silence_time(segments, len_frames):
    frame_count = 0
    for i, segment in enumerate(segments):
        frame_count += segment[1]

    clip_all_time = len_frames * config['frame_duration_ms']
    clip_remain_time = frame_count * config['frame_duration_ms']
    clip_silence_time = (len_frames - frame_count) * config['frame_duration_ms']
    print('all time: ', clip_all_time)
    print('remain time: ', clip_remain_time)
    print('remove time: ', clip_silence_time)

    return clip_all_time, clip_remain_time, clip_silence_time

# interface function
# input: audio path
# output: audio silence time
def get_audio_silence(audio_path):
    assert os.path.isfile(audio_path)
    audio, sample_rate = read_wave(audio_path)
    vad = webrtcvad.Vad(config['sensitivity'])
    frames = frame_generator(config['frame_duration_ms'], audio, sample_rate)
    frames = list(frames)
    len_frames = len(frames)
    segments = vad_collector(sample_rate, config['frame_duration_ms'], config['padding_duration_ms'], vad, frames)

    frame_all_time, frame_remain_time, frame_silence_time = get_frame_silence_time(frames, vad, sample_rate)
    clip_all_time, clip_remain_time, clip_silence_time = get_clip_silence_time(segments, len_frames)

    return frame_silence_time, clip_silence_time

if __name__ == '__main__':
    frame_remove_time, clip_remove_time = get_audio_silence(config['audio_path'])

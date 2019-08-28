%% clear
clear all; close all; clc;

audio_path = '/home/lei/音乐/移出静音结果/短时能量+阀值/audio_path.txt';
%audio_path = '/home/lei/桌面/other.txt';
disp('123');
%write_dir_path = '/home/lei/音乐/移出静音结果/短时能量+阀值/move_silence_frame_7ms/win_7/move_silence_3/';
move_dir_path = '';
%write_remove_dir_path = '/home/lei/音乐/移出静音结果/短时能量+阀值//music_removed/';
fr = fopen(audio_path);
audio_path_list = textscan(fr, '%s');
fclose(fr);
audio_path_list = audio_path_list{1};

for m=1:length(audio_path_list)
    audio_path = audio_path_list{m};
    remove_slicen(audio_path, write_dir_path);
end

function remove_slicen(audio_path, write_dir_path)
    wav = audioread(audio_path, 'native');
    wav_info = audioinfo(audio_path);
    
    %% extract frames
    frame_length_ms = 7; %25 %9
    frame_shift_ms = 7;  %10 %9
    num_of_frames = floor((wav_info.Duration * 1000 - frame_length_ms) / frame_shift_ms);
    len_of_frames = frame_length_ms * wav_info.SampleRate / 1000;

    wav_frames = zeros(num_of_frames, len_of_frames);
    for f = 1:num_of_frames
        idx = (f - 1) * frame_shift_ms * wav_info.SampleRate / 1000 + 1;    % index start from 1, not 0
        wav_frames(f,:) = wav(idx:idx+len_of_frames-1);
    end
    
    %% zero-crossing rate
    zcr = zeros(num_of_frames, 1);
    zer_temp = [];
    for f = 1:num_of_frames
        zcr(f) = 1 / 2 * sum(abs(wav_frames(f,2:len_of_frames) - ...
                             wav_frames(f,1:len_of_frames-1)));

    end
    %figure;
    %subplot(3,1,1); plot(wav); title('wavform'); hold on;
    %subplot(3,1,2); plot(zcr); title('zero-crossing rate'); hold on;
    %subplot(3,1,3); plot(zer_temp); title('zero-crossing rate'); hold on;
    
    %% energy
    energy = zeros(num_of_frames, 1);
    for f = 1:num_of_frames
        energy(f) = sum(power(wav_frames(f,:),2));
        %disp("==========");
        %disp(energy(f));
        %if energy(f) >= threshold
        %    idx = (f - 1) * frame_shift_ms * wav_info.SampleRate / 1000 + 1;
        %    energy_win_copy = [energy_win_copy; wav(idx:idx+len_of_frames-1)];
        %    %disp(size(energy_win_copy))
        %    %disp(sds)
        %end
    end
    
    %% energy + window
    %vad_energy_mean_scale = 1;%0.2
    %vad_frames_context = 4;     % window_size = 2 * vad_frames_context + 1;
    %vad_proportion_threshold = 0.5;%0.15
    %energy_win = zeros(num_of_frames, 1);
    %energy_win_copy = [];
    %energy_win_other = [];
    vad_energy_threshold = 0;%700000
    vad_energy_mean_scale = 0.0001;%0.2
    vad_frames_context = 3;     % window_size = 2 * vad_frames_context + 1;
    vad_proportion_threshold = 0.2;%0.15 %0.5
    energy_win = zeros(num_of_frames, 1);
    zcr_win = zeros(num_of_frames, 1);
    energy_win_copy = [];
    energy_win_other = [];

    vad_energy_threshold = vad_energy_threshold + vad_energy_mean_scale * mean(energy);
    zcr_threshold = 1800;%1000
    f_list = [];
    final_list = [];
    before_after = 3;
    for f = 1:num_of_frames
        win_s = max(1, f - vad_frames_context);
        win_e = min(num_of_frames, f + vad_frames_context);
        zcr_win(f) = (zcr(f) > zcr_threshold);
        energy_win(f) = ((sum(energy(win_s:win_e) > vad_energy_threshold) >= (2 * vad_frames_context + 1)*vad_proportion_threshold));
        if energy_win(f) && zcr_win(f)
            f_list = [f_list f];
        end
    end
    
    for index = 1:length(f_list)
        if f_list(index) > before_after
            before = f_list(index) - before_after;
        else
            before = 1;
        end
        if f_list(index) < num_of_frames - before_after+1
            after = f_list(index) + before_after;
        else
            after = num_of_frames;
        end
        final_list = [final_list before f_list(index) after];
    end
    
    length_original = length(f_list);
    length_save = length(final_list);
    length_remove = length_original - length_save;
    if length_remove > thread_length
        copyfile(audio_path, );
    end
    
    
    % %disp(final_list);
    % %disp('====');
    % final_list = unique(final_list);
    % %disp(final_list);
    % for index_f = 1:length(final_list)
    %     %disp(index_f);
    %     %disp(final_list(index_f));
    %     idx = (final_list(index_f) - 1) * frame_shift_ms * wav_info.SampleRate / 1000 + 1;
    %     %disp(idx)
    %     energy_win_copy = [energy_win_copy; wav(idx:idx+len_of_frames-1)];
    % end

        
    %%figure
    %figure;
    %disp(min(energy));
    %subplot(4,1,1); plot(wav); title('wavform'); hold on;
    %subplot(4,1,2); plot(energy_win); title('energy_win');
    %subplot(4,1,3); plot(energy_win_copy); title('energy_win_copy');hold on;
    %subplot(4,1,4); plot(energy_win_other); title('energy_win_other');
    audio = strsplit(audio_path, '/');
    %audio_folder = audio(length(audio)-1);
    audio_name = audio(length(audio));
    audio_class = audio(length(audio)-1);
    
    %disp(write_dir_path);disp(audio_name);
    remain_write_path = strcat(write_dir_path, audio_class, '/', audio_name);
    %remove_write_path = strcat(write_remove_dir_path, audio_name);
    %disp(remain_write_path);
    if length(energy_win_copy) > 0
        audiowrite(remain_write_path{1}, energy_win_copy, 8000);
    end
    %if length(energy_win_other) > 0
    %    audiowrite(remove_write_path{1}, energy_win_other, 8000);
    %end
    
end

%form web: https://blog.csdn.net/wxb1553725576/article/details/78069089

% vad_energy_threshold = 881500;除去全杂音的那个

%噪音大概值: 877851
% 正常对话善删掉中间
% 2019010375518532736.wav
% vad_energy_threshold = 169000;%165000
% vad_energy_mean_scale = 0.8;
% vad_proportion_threshold = 0.5;

% 只有客服说，客户不答
% 2019010775518828184.wav
% vad_energy_threshold = 169000;
% vad_energy_mean_scale = 0.8;
% vad_proportion_threshold = 0.5;

% 完全杂音
% 2019010275518347138.wav
% vad_energy_threshold = 179000;
% vad_energy_mean_scale = 0.8;
% vad_proportion_threshold = 0.5;

%% clear
clear all; close all; clc;

%% read wav
%filename = '/home/lei/下载/sx438.wav';
filename = '/home/lei/data/upload_chang/yueyu/yy_2018082520001403111_副本.wav';%2019010375518532736.wav
wav = audioread(filename, 'native');
wav_info = audioinfo(filename);
%disp(wav_info.SampleRate);
%figure; plot(wav); title('wavform'); hold on;

%% extract frames
frame_length_ms = 5; %25
frame_shift_ms = 5;  %10
num_of_frames = floor((wav_info.Duration * 1000 - frame_length_ms) / frame_shift_ms);
len_of_frames = frame_length_ms * wav_info.SampleRate / 1000;

wav_frames = zeros(num_of_frames, len_of_frames);
for f = 1:num_of_frames
    idx = (f - 1) * frame_shift_ms * wav_info.SampleRate / 1000 + 1;    % index start from 1, not 0
    wav_frames(f,:) = wav(idx:idx+len_of_frames-1);
end

%% sum(abs())
amplitudes = zeros(num_of_frames, 1);
for f = 1:num_of_frames
    amplitudes(f) = sum(abs(wav_frames(f,:)));
end
figure;
subplot(2,1,1); plot(wav); title('wavform'); hold on;
subplot(2,1,2); plot(amplitudes); title('amplitudes'); hold on;

%% energy
threshold = 0;
energy_win_copy=[];

energy = zeros(num_of_frames, 1);
for f = 1:num_of_frames
    energy(f) = sum(power(wav_frames(f,:),2));
    %disp("==========");
    %disp(energy(f));
    if energy(f) >= threshold
        idx = (f - 1) * frame_shift_ms * wav_info.SampleRate / 1000 + 1;
        energy_win_copy = [energy_win_copy; wav(idx:idx+len_of_frames-1)];
        %disp(size(energy_win_copy))
        %disp(sds)
    end
end
%disp("energy.mean");
%disp(mean(energy));
figure;
subplot(4,1,1); plot(wav); title('wavform'); hold on;
subplot(4,1,2); plot(amplitudes); title('amplitudes'); 
subplot(4,1,3); plot(energy); title('energy'); 
subplot(4,1,4); plot(energy_win_copy); title('energy_win_copy');hold on;

%% zero-crossing rate
zcr = zeros(num_of_frames, 1);
zer_temp = [];
for f = 1:num_of_frames
    zcr_f = 1 / 2 * sum(abs(wav_frames(f,2:len_of_frames) - ...
                             wav_frames(f,1:len_of_frames-1)));
    %disp(zcr_f);
    zcr(f) = zcr_f;
    if zcr_f > 1800
        zer_temp = [zer_temp zcr_f];
    end
end
figure;
subplot(3,1,1); plot(wav); title('wavform'); hold on;
subplot(3,1,2); plot(zcr); title('zero-crossing rate'); hold on;
subplot(3,1,3); plot(zer_temp); title('zero-crossing rate'); hold on;

%% energy + window
vad_energy_threshold = 0;%700000
vad_energy_mean_scale = 0.0001;%0.2
vad_frames_context = 3;     % window_size = 2 * vad_frames_context + 1;
vad_proportion_threshold = 0.2;%0.15
energy_win = zeros(num_of_frames, 1);
zcr_win = zeros(num_of_frames, 1);
energy_win_copy = [];
energy_win_other = [];

%i=1;
%vad_energy_threshold = vad_energy_threshold + vad_energy_mean_scale * mean(energy);
%vad_energy_threshold = vad_energy_threshold + vad_energy_mean_scale * mean(energy);
vad_energy_threshold = 10000;
zcr_threshold = 1800;%1000
f_list = [];
final_list = [];
before_after = 3;
for f = 1:num_of_frames
    win_s = max(1, f - vad_frames_context);
    win_e = min(num_of_frames, f + vad_frames_context);
    
    %disp('energy(win_s:win_e)');
    %disp(energy(win_s:win_e));
    %disp('vad_energy_threshold');
    %disp(vad_energy_threshold);
    %disp('sum(energy(win_s:win_e) > vad_energy_threshold)');
    %disp(sum(energy(win_s:win_e) > vad_energy_threshold));
    %disp((2 * vad_frames_context + 1)*vad_proportion_threshold);
    disp("===========");
    disp(energy(win_s:win_e));
    disp(vad_energy_threshold);
    disp((2 * vad_frames_context + 1)*vad_proportion_threshold);
    disp(sum(energy(win_s:win_e) > vad_energy_threshold));
    %disp('==================');
    %disp(f);
    %disp(zcr_win(f));
    %disp(energy_win(f));
    %disp(energy_win(f) && zcr_win(f));
    zcr_win(f) = (zcr(f) > zcr_threshold);
    energy_win(f) = ((sum(energy(win_s:win_e) > vad_energy_threshold) >= (2 * vad_frames_context + 1)*vad_proportion_threshold));
    %disp(gfdg);
    %energy_win_sil(f) = ((sum(energy(win_s:win_e) > vad_energy_threshold) >= (2 * vad_frames_context + 1)*vad_proportion_threshold));
    %disp(energy_win(f));
    %disp(sdf);
    if energy_win(f) && zcr_win(f)
        f_list = [f_list f];
        %idx = (f - 1) * frame_shift_ms * wav_info.SampleRate / 1000 + 1;
        %energy_win_copy = [energy_win_copy; wav(idx:idx+len_of_frames-1)];
    %energy_win_copy = [energy_win_copy wav((f-1)*frame_shift_ms: f*frame_shift_ms)];
    %    i = i +1;
    %else
    %    energy_win_other = [energy_win_other; wav(idx:idx+len_of_frames-1)];
    end
end

%disp(f_list(1) - before_after);
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
%disp(final_list);
%disp('====');
final_list = unique(final_list);
%disp(final_list);
for index_f = 1:length(final_list)
    %disp(index_f);
    %disp(final_list(index_f));
    idx = (final_list(index_f) - 1) * frame_shift_ms * wav_info.SampleRate / 1000 + 1;
    %disp(idx)
    energy_win_copy = [energy_win_copy; wav(idx:idx+len_of_frames-1)];
end


figure;
%disp(min(energy));
subplot(3,1,1); plot(wav); title('wavform'); hold on;
subplot(3,1,2); plot(energy_win); title('energy_win');
subplot(3,1,3); plot(energy_win_copy); title('energy_win_copy');hold on;
%subplot(4,1,4); plot(energy_win_other); title('energy_win_other');
audiowrite('all_test_1.wav', energy_win_copy, 8000);
%audiowrite('all_test_other_1.wav', energy_win_other, 6000);

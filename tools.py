import mne
import pandas as pd
import matplotlib
import numpy as np
import json

def read_events_df(name, event_label):
    events = json.load(open(name))
    events_values = [(e['time'], event_label(e), e) for e in events]
    events_df = pd.DataFrame(events_values[1:], columns=["time", "label", "json"])
    events_df["time"] = pd.to_datetime(events_df["time"]).dt.strftime("%H:%M:%S.%f").apply(lambda x: x[:-5])
    return events_df

def read_signal(name, ch_names, ch_types, sampling_freq):
    signal_df = pd.read_csv(
        name,
        sep=", ", skiprows=6, names=["#"] + ch_names + ["x", "y", "z", "time", "timestamp"]
    )
    signal_df = signal_df.iloc[1:-1].copy()
    signal_df["time"] = pd.to_datetime(signal_df["time"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    
    signal_info = mne.create_info(ch_names, ch_types=ch_types, sfreq=sampling_freq)
    signal_info.set_montage('standard_1020')
    signal_info["start_time"] = signal_df["time"].min()
    
    data = signal_df[ch_names].values.T
    raw = mne.io.RawArray(data, signal_info)
    raw.notch_filter(50, notch_widths=3)
    raw.filter(1, 50)
    
    return raw

def get_alpha_amplitude(raw, sampling_freq, channels, stim_channel_name=None):
    channel_raw = raw.copy().pick(channels).get_data(channels).mean(axis=0)
    raw = raw.copy().filter(7, 13)
    channel_alpha = raw.get_data()[0]
    alpha_amplitude = pd.Series(np.abs(channel_alpha))\
        .rolling(sampling_freq * 3, center=True).quantile(0.6).fillna(0).tolist()
    alpha_std = pd.Series(np.abs(channel_alpha))\
        .rolling(sampling_freq * 3, center=True).std().fillna(0).tolist()
    
    if not stim_channel_name:
        stim_channel = np.zeros(channel_alpha.shape[0])
        event_duration = 10 * sampling_freq
        stim_channel[np.where(np.arange(stim_channel.shape[0]) % event_duration == 0)] = 1

        stim_channel[np.where(
            (stim_channel.cumsum() % 2 == 0) & \
            (stim_channel > 0)
        )] += 1
    else:
        stim_channel = raw.copy().pick([stim_channel_name]).get_data([stim_channel_name]).reshape(-1)
    
    signal_info = mne.create_info(
        ["channel", "rhythm", "amplitude", "std", "stim"], 
        ch_types=["eeg", "eeg", "misc", "misc", "stim"], 
        sfreq=sampling_freq
    )
    signal_info["start_time"] = raw.info["start_time"]
    
    data = [channel_raw, channel_alpha, alpha_amplitude, alpha_std, stim_channel]
    
    return mne.io.RawArray(data, signal_info)

def plot_frequencies(raw, frequencies, start, duration):
    raw = raw.copy().filter(*frequencies)
    old_rc = matplotlib.rcParams["figure.figsize"]
    matplotlib.rcParams["figure.figsize"] = (20, 10)
    mne.viz.plot_raw(
        raw,
        start=start, 
        duration=duration, 
        show_scalebars=False, 
        scalings={"eeg": 30},
        show=False
    )
    matplotlib.rcParams["figure.figsize"] = old_rc
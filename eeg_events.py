import datetime as dt
import mne
import pandas as pd


def get_paths(name):
    return (
        f"./valid-data/processed/{name}-unprocessed.raw.fif",
        f"./valid-data/processed/events-{name}.csv",
        f"./valid-data/processed/{name}.raw.fif"
    )

def save_events(raw, raw_alpha, events_df, name):
    raw_path, events_path, raw_alpha_path = get_paths(name)
    
    record_date = raw.info["start_time"].split()[0]
    record_start_time = dt.datetime.strptime(raw.info["start_time"], "%Y-%m-%d %H:%M:%S")
    
    events_df["datetime"] = pd.to_datetime(record_date + " " + events_df["time"])
    events_df["timestamp"] = (events_df["datetime"] - record_start_time).dt.total_seconds().astype(int)
    
    raw.save(raw_path, overwrite=True)
    raw_alpha.save(raw_alpha_path, overwrite=True)
    events_df.to_csv(events_path, index=False)
    
def iterate_events(name, duration=1):
    events_path, raw_path = get_paths(name)
    
    raw = mne.io.read_raw_fif(raw_path)
    events_df = pd.read_csv(events_path)
    
    frequency = int(raw.info["sfreq"])
    for i, row in events_df.iterrows():
        try:
            event_data = raw.get_data(
                picks="misc", 
                start=row["timestamp"] * frequency,
                stop=(row["timestamp"] + duration) * frequency
            ).mean(axis=0)
            yield row["timestamp"], eval(row["json"]), event_data
        except:
            break
            
            
from __future__ import annotations
from data import get_csv_paths
import pandas as pd
import numpy as np
import re

class AZ_DF():

    def __init__(self):
        csv_paths = get_csv_paths()
        
        NA_STRINGS = [
            "Not specified", "not specified", "Not Specified",
            "Not included", "not included", "Not Included",
            "Not applicable", "not applicable", "Not Applicable",
            "Unknown", "unknown", "?", "? m", "?? m", "Unknown m", "unkown m", "- m", " m", "-", "--", "none", "null", "Null", "n.a.", "N.A.",
            "0000-00-00", "?:?", "xx:xx", "am", "pm", ".", "x",
        ]
    
        self.xc_am_df = pd.read_csv(csv_paths["A-M"], na_values=NA_STRINGS, low_memory=False)
        self.xc_nz_df = pd.read_csv(csv_paths["N-Z"], na_values=NA_STRINGS, low_memory=False)
    
    def get_az(self):
        self.drop()
        self.encode_self()
        self.columns_to_num()

        self.xc_am_df["elevation"] = self.xc_am_df["elevation"].apply(self.parse_elevation)
        self.xc_nz_df["elevation"] = self.xc_nz_df["elevation"].apply(self.parse_elevation)

        xc_az_df = pd.concat([self.xc_am_df, self.xc_nz_df], ignore_index=True).drop_duplicates(subset=["ebird_code", "filename"], ignore_index=True)

        if len(xc_az_df.columns)>23:
            RuntimeError("issue: ",len(xc_az_df.columns))

        return xc_az_df


    def parse_elevation(self, s):
        """Elevation text -> meters (float), or NaN when there's no usable number."""
        if pd.isna(s):
            return np.nan
        s = s.replace(",", "")                                    # '1,105' -> '1105'

        # Forcing claude to reevaluate naming conventions - multi seems to have been meant for multiple decimal points
        multi = re.search(r"(\d+)\.(\d+(?:\.\d+)+)", s)           # '564.676.941' -> '564.676941'
        if multi:
            s = s.replace(multi.group(0), multi.group(1) + "." + multi.group(2).replace(".", ""))

        #rng to avoid keyword range
        rng = re.search(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", s)
        if rng:                                                   # '2750-3250' -> 3000 (midpoint)
            return (float(rng.group(1)) + float(rng.group(2))) / 2

        #previously named 'one' to indicate singular num and not a range -- variable renamed to negative for readability
        negative = re.search(r"-?\d+(?:\.\d+)?", s)                    # '-30 m' stays negative
        return float(negative.group()) if negative else np.nan

    def parse_time(self, xc_df):
        parts = xc_df['time'].str.extract(
            r'^\s*0*(\d{1,2})\s*[;:.h]\s*(\d{2})(?::\d{2})?\s*(am|pm)?\s*$', flags=re.IGNORECASE)

        #changed h and m to hours and minutes
        hours = pd.to_numeric(parts[0], errors='coerce')
        minutes = pd.to_numeric(parts[1], errors='coerce')

        ampm = parts[2].str.lower()
        hours = hours.where(~((ampm == 'pm') & (hours < 12)), hours + 12)   # 7:30 pm -> 19:30
        hours = hours.where(~((ampm == 'am') & (hours == 12)), 0)       # 12:15 am -> 00:15


        hours = hours.where(hours != 24, 0)

        #this is the part where claude removes what it thinks are invalid times
        valid = hours.between(0, 23) & minutes.between(0, 59)
        return hours, minutes, valid

    def drop(self):
        #Dropping columns with redundant info
        drop_list=['title', 'sci_name', 'xc_id', 'url', 'author', 'license', 'file_type']
        self.xc_am_df.drop(drop_list,axis=1,inplace=True)
        self.xc_nz_df.drop(drop_list, axis=1, inplace=True)

    def encode_self(self):
        #using dummies to onehot encode bird seen or not seen -- Nan is marked as not seen 0
        self.xc_am_df = pd.concat([self.xc_am_df, pd.get_dummies(self.xc_am_df['bird_seen'], dummy_na=False, prefix="bird_seen", dtype=int)], axis =1)
        self.xc_am_df.drop(['bird_seen'], axis=1, inplace=True)

        self.xc_nz_df = pd.concat([self.xc_nz_df, pd.get_dummies(self.xc_nz_df['bird_seen'], dummy_na=False, prefix="bird_seen", dtype=int)], axis =1)
        self.xc_nz_df.drop(['bird_seen'], axis=1, inplace=True)

        #using dummies to onehot encode playback_used or not -- Nan is marked as not seen 0
        self.xc_am_df = pd.concat([self.xc_am_df, pd.get_dummies(self.xc_am_df['playback_used'], dummy_na=False, prefix="playback_used", dtype=int)], axis =1)
        self.xc_am_df.drop(['playback_used'], axis=1, inplace=True)

        self.xc_nz_df = pd.concat([self.xc_nz_df, pd.get_dummies(self.xc_nz_df['playback_used'], dummy_na=False, prefix="playback_used", dtype=int)], axis =1)
        self.xc_nz_df.drop(['playback_used'], axis=1, inplace=True)

    def columns_to_num(self):
        # rating 0 = never rated on xeno-canto, not "worst quality" -> NaN
        self.xc_am_df["rating"] = self.xc_am_df["rating"].replace(0.0, np.nan)
        self.xc_nz_df["rating"] = self.xc_nz_df["rating"].replace(0.0, np.nan)

        #mono and stereo are described as one or two
        for col in ["channels", "sampling_rate", "bitrate_of_mp3"]:
            self.xc_am_df[col] = self.xc_am_df[col].str.extract(r"^(\d+)", expand=False).astype("Int64")
            self.xc_nz_df[col] = self.xc_nz_df[col].str.extract(r"^(\d+)", expand=False).astype("Int64")

        am_hours, am_minutes, am_valid = self.parse_time(self.xc_am_df)
        self.xc_am_df['time'] = (am_hours + am_minutes / 60).where(am_valid).round(2)
        nz_hours, nz_minutes, nz_valid = self.parse_time(self.xc_nz_df)
        self.xc_nz_df['time'] = (nz_hours + nz_minutes / 60).where(nz_valid).round(2)

        self.xc_am_df.rename(columns={'time':'hours_from_midnight',
                                    'bitrate_of_mp3':'bitrate_bps',
                                    'sampling_rate':'sampling_rate_hz'}, inplace=True)
        self.xc_nz_df.rename(columns={'time':'hours_from_midnight',
                                        'bitrate_of_mp3':'bitrate_bps',
                                        'sampling_rate':'sampling_rate_hz'}, inplace=True)
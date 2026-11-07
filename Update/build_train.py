import librosa
import pandas as pd
from Update.clean_df import AZ_DF
from Update.data import get_dataset_path

class Train_DF():
    def __init__(self):
        cleaner = AZ_DF()
        self.az_df = cleaner.get_az()
        self.embed_df = None
        self.roots = {"A-M": get_dataset_path("A-M"), "N-Z": get_dataset_path("N-Z")}

    def get_embedding_df(self):
        self.sf_sac_filter()
        self.min_50_trim()
        self.add_paths()

        return self.embed_df

    def save_embedding_as_pickle(self):
        self.embed_df.to_pickle("./embed_df.pkl")

    def get_embedding_from_pickle(self):
        self.embed_df = pd.read_pickle("./embed_df.pkl")  #loads pickle from local dir

    def sf_sac_filter(self):
        df = self.az_df

        in_region = df["latitude"].between(37.2, 39.8) & df["longitude"].between(-123.0, -119.5)
        region_species = df.loc[in_region, "ebird_code"].unique()

        self.embed_df = df[df["ebird_code"].isin(region_species) & (df["rating"] >= 3.5)]

    def min_50_trim(self):
        eligible = self.embed_df[(self.embed_df["sampling_rate_hz"] >= 16000)]

        counts = eligible["ebird_code"].value_counts()                  # changed: count eligible
        keep = counts[counts >= 50].index
        eligible = eligible[eligible["ebird_code"].isin(keep)]         # changed: filter eligible

        selected_df = (
            eligible
            .assign(
                is_mono=eligible["channels"].eq(1),
                is_16k=eligible["sampling_rate_hz"].eq(16000),
            )
            .sample(frac=1, random_state=42)
            .sort_values(["is_mono", "is_16k", "rating"], ascending=False, kind="stable")
            .groupby("ebird_code")
            .head(50)
            .drop(columns=["is_mono", "is_16k"])
            .reset_index(drop=True)
        )

        self.embed_df = selected_df

    def get_path(self, row):
        split = "A-M" if row["ebird_code"][0].lower() <= "m" else "N-Z"
        
        recording_path = f"{split}/{row['ebird_code']}/{row['filename']}"

        return self.roots[split] / recording_path
    
    def add_paths(self):
        self.embed_df['recording_path'] = self.embed_df.apply(self.get_path, axis=1)

    def add_embeddings(self):
        pass
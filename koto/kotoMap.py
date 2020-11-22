import keplergl
import json
import pandas as pd

class geo_map:

    def __init__(self, height:int=500, config_file:str="data/kepler_initial_config.json"):
        with open("data/kepler_initial_config.json") as json_data_file:
            kepler_config = json.load(json_data_file)
        self.map = keplergl.KeplerGl(height=height, config = kepler_config)

    def add_default_data(self, candidates:bool=True,selections:bool=True,raw_dests:bool=True):
        if candidates:
            dens_df = pd.read_csv("data/dens_df.csv")
        if selections:
            cluster_selection_df = pd.read_csv("data/cluster_selection_df.csv")
        if raw_dests:
            dest_raw_df = pd.read_csv("data/dest_raw_df.csv", index_col=[0])
        self.map.add_data(data=dens_df, name="Candidate Locations")
        self.map.add_data(data=cluster_selection_df, name="Selected Clusters")
        self.map.add_data(data=dest_raw_df, name="Destinations Raw")

    def add_data(self, dataframe, name:str="UserSpecifiedData"):
        self.map.add_data(dataframe, name=name)
        print(f"{name} added!")
    
    def show(self):
        return self.map

    def export_to_html(self, file_name:str="UserKotoMapExport.html", read_only:bool=False):
        self.map.save_to_html(file_name=file_name, read_only=read_only)
import os
from model import GI_individual as us
import pandas as pd

areas=pd.read_csv('model/building_areas')

storms=['M5y10h','M50y10h','M200y10h','M10000y10h']
subcatchments=[[i] for i in list(areas['Name'])]

for s in storms:
    filename=f'Topsham{s}'
    output=us.set_simulGI_node('BioCell',subcatchments,16,filename)
    us.save_results('BioCell', s, output) 
    
    
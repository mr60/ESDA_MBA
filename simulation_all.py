import os
from model import GI_all as us
import pandas as pd

areas=pd.read_csv('model/building_areas')

storms=['M2y10h','M5y10h','M10y10h','M30y10h','M50y10h','M100y10h','M1000y10h','M10000y10h']
subcatchments=[[i] for i in list(areas['Name'])]

for s in storms:
    filename=f'Topsham{s}'
    output=us.set_simulGI_node('all',subcatchments,16,filename)
    us.save_results('all', s, output) 
    
 
import os
from model import use_scenarios as us
storms=[i for i in os.listdir('storms/') if i.startswith('M')]

use=[[5],[10],[25],[50],[75],[100]]

for s in storms:
    filename=f'Topsham{s}'
    output=us.set_simulGI_node('BioCell',use,16,filename)
    us.save_results('BioCell',use, s, output)
      
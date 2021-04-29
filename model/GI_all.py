'''
                                            ,~~_
                                            |/\ =_ _ ~
                                             _( )_( )\~~
                                             \,\  _|\ \~~~
                                                \`   \
                                                `    `

                                    University of EXETER, 2021
                                           
                                           Mayra Rodriguez
                                           QUEX INSTITUTE

Simulation set-up 

Includes,
1. Modification of the input file
2. Result extraction
3. Parallelisation of the simualtion
4. Save results

'''

# ----------
# PACKAGES #
# ----------

import pandas as pd
from pyswmm import Simulation, Nodes, Subcatchments
from model import swmmtb as st
from tqdm import tqdm
import os

#Subcatchmentinfo
from model import sections as sec
df=sec.import_inputfile('topsham_ag.inp')
inputer=sec.deteriminesections(df)

for index, row in inputer['subcatchments'].iterrows():
    if 0<=row['Width']<1:
        df.loc[index,'Width']=1
for index, row in inputer['subcatchments'].iterrows():
    inputer['subcatchments'].loc[index,'Name']=row['Name'].strip()
    
areas=pd.read_csv('model/building_areas')

areas[['%Imperv', 'total_area','imperv_area', 'perv_area', 'build_area']]=areas[['%Imperv', 'total_area','imperv_area', 'perv_area', 'build_area']].astype(float)

inputer['subcatchments']['%Imperv']=areas['%Imperv']
    
    
def LIDGIsubcat_area(use, filename, subcatchments):
    '''
    Modifies the input file dataframe and sets the usage of GI in the different subcatchments

    Inputs
    -----
    use: percentage to be used in GI per subcatchment. 
    
    
    filename: swmm input file name as a string in the form of a dataframe
    
    
    subcatchment:list of subcatchments


    Note: the use is a porcentage.

    Output
    ------
    Swmm input file modified
    '''
    areas=pd.read_csv('model/building_areas')

    areas[['%Imperv', 'total_area','imperv_area', 'perv_area', 'build_area']]=areas[['%Imperv', 'total_area','imperv_area', 'perv_area', 'build_area']].astype(float)
    
    theinputer=pd.read_csv('input_files/'+filename+'.inp', header=None, skip_blank_lines=False)
    #--------------------------------------------------------------
    
    lid=pd.DataFrame()
    
    areas=areas[areas['Name'].isin(subcatchments)].copy()
    
    #LID INFORMATION
    lid['Subcat']=[areas['Name'].values[0], areas['Name'].values[0],areas['Name'].values[0]]
    lid['LID']=['BioCell', 'GreenRoof','PerPav']
    lid['Number']=[1,1,1]
    lid['Area']=[areas['perv_area'].values[0]*(use/100),(areas['build_area'].values[0]*(use/100)),(areas['imperv_area']-areas['build_area']).values[0]*(use/100)]
    lid['Width']=[1,1,1]
    lid['InitSat']=[0,0,0]
    lid['FromImp']=[1,0,0]
    lid['ToPerv']=[0,1,0]
    
    lid=lid.fillna(0)
   
    #Add data about LID usage based on use and lid type
    indGI=theinputer.index[theinputer[0]=='[LID_USAGE]'] 
    locGI=theinputer.index.get_loc(indGI[0])

    data=lid.round(2).astype(str)+'\t'
    data_strings = pd.DataFrame(data.values.sum(axis=1))

    #Insert new data
    dfA=theinputer[theinputer.index<= locGI+2]
    dfB=theinputer[theinputer.index>locGI+3]

    theinputermodified=dfA.append(data_strings, ignore_index=True)
    theinputermodified=theinputermodified.append(dfB, ignore_index=True)
    
    
    #CHANGE IN IMPERVIOUSNESS
    #Index information Subcatchments
    indsub=theinputermodified.index[theinputermodified[0]=='[SUBCATCHMENTS]']
    ind2sub=theinputermodified.index[theinputermodified[0]=='[SUBAREAS]']
    locsub=theinputermodified.index.get_loc(indsub[0])
    loc2sub=theinputermodified.index.get_loc(ind2sub[0])
    
    #set %impervious as floating number
    df=inputer['subcatchments'].copy()
    df[['%Imperv','Area']] = df[['%Imperv','Area']].astype(float)

    #Change imperviousness
    for index, row in df.iterrows():
        if row['Name'] in subcatchments:
            df.loc[index,'%Imperv']=0
            df.loc[index,'Area']=(1/10000)*(areas['perv_area']+areas['imperv_area']).values[0]
      

    #Data series new rainfall data
    data=df.round(5).astype(str)+'\t'
    data_strings = pd.DataFrame(data.values.sum(axis=1))

    #Insert new data
    dfA=theinputermodified[theinputermodified.index<= locsub+2]
    dfB=theinputermodified[theinputermodified.index>=loc2sub]

    theinputermod=dfA.append(data_strings, ignore_index=True)
    theinputermod=theinputermod.append(dfB, ignore_index=True)

    fin='input_files/'+filename+str(hash(''.join(subcatchments)))+f'use_{use}'+'.inp'

    theinputermod.to_csv(fin,header=False, index=False, quoting=3, sep='\n', na_rep=' ')

def result_extract(filename):
    '''
    This funciton extracts the flooding time series
    
    INPUT
    -----
    Filename: string without the extension. 
    
    OUTPUT
    ------
    Pandas dataframe where each column is named after 
    '''
    floodnode={}
    with Simulation('input_files/'+filename+'.inp') as sim:
        for node in tqdm(Nodes(sim)):
            floodnode[node.nodeid]=st.extract('input_files/'+filename+'.out',['node', node.nodeid, 'Flow_lost_flooding'])
    
    print('Flood Extraction Done!')
    
    for key, value in floodnode.items():
        value.rename(columns={'node_{}_Flow_lost_flooding'.format(key):key},inplace=True)
        
    floodrate=pd.DataFrame()
    floodrate['timestamp']=floodnode[list(floodnode.keys())[0]].index
    
    for key, value in tqdm(floodnode.items()):
        floodrate[key]=value[key].values
        
    CSO_flow=st.extract('input_files/'+filename+'.out',['node','SX96882104','Total_inflow'])
    CSO_flow=CSO_flow.reset_index().rename(columns={'index':'timestamp'})
    
    
    WWTP_flow=st.extract('input_files/'+filename+'.out',['node','SX94899203','Total_inflow'])
    WWTP_flow=WWTP_flow.reset_index().rename(columns={'index':'timestamp'})
    "CSO & WWTP flows done"
    
    return floodrate.drop(range(500,floodrate.count()[0])), CSO_flow, WWTP_flow


def simulGI_nodes(i,filename):
    '''
    Function to be iterated using parallelisation
    Filename needs to be changed every time that the storm is changed
    
    Input
    -----
    i: list of subcatchments where GI will be implemented
    filename: filename without extention

    Output
    ------
    Pandas dataframe where the columns are the nodes time series
    
    '''
    use=100
    
    LIDGIsubcat_area(use,filename,i)

    fin=filename+str(hash(''.join(i)))+f'use_{use}'

    sim=Simulation('input_files/'+fin+'.inp')
    sim.execute()

    res,cso,wwtp=result_extract(fin)
    print('Result extraction done!')

    os.remove('input_files/'+fin+'.inp')
    os.remove('input_files/'+fin+'.out')
    os.remove('input_files/'+fin+'.rpt')

    print('Files removed!')

    return [res,cso,wwtp]

def simulGI_nodes_unpack(args):
    return simulGI_nodes(*args)

def set_simulGI_node(j, rs, num_processors,filename):
    '''
    Input
    ------
    j: use % GI in the subcatchment
    rs: random sequence -- each element of the list is a list.
    num_processors: the number of processors to be used - MAX 20
    
    Output
    ------
    output: results in the form of a list, where the elements are pandas dataframes
    '''
    
    from multiprocessing import Pool
    import time
    import itertools
    
    start=time.time()    
    p=Pool(num_processors)
    output=p.map(simulGI_nodes_unpack,zip(rs,itertools.repeat(filename)))
    p.close()

    elapsed=start-time.time()
    print(f'RES Simulation use_{j} finished at time {elapsed}.')

    return output

def save_results(j,storm,output):
    '''
    This functions saves the results obtained in the parallelized simulations
    
    Input
    ------
    j: simulation number
    rs: random/non-random list of subcatchments used
    storm: the storm used in the input file
    output: the result of the parallelised simulation
    
    
    Output
    ------
    Set of CSV with the result of each simulation
    '''
    
    results=['flood','cso','wwtp']
    
    for i in range(0, len(output)):
        for m in range(0,len(results)):
            output[i][m].to_csv(f'results/all/simulation_{storm}_use100_{j}_{i}_{results[m]}')

     
    print(f'Results saved for simulation use_{j}')
'''
                                            ,~~_
                                            |/\ =_ _ ~
                                             _( )_( )\~~
                                             \,\  _|\ \~~~
                                                \`   \
                                                `    `

                                    University of EXETER, 2020
                                           
                                           Mayra Rodriguez

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
df=sec.import_inputfile('input_files/Topsham.inp')
inputer=sec.deteriminesections(df)
for index, row in inputer['subcatchments'].iterrows():
    if 0<=row['Width']<1:
        df.loc[index,'Width']=1
for index, row in inputer['subcatchments'].iterrows():
    inputer['subcatchments'].loc[index,'Name']=row['Name'].strip()
    
def LIDGIsubcat_area(area, typeGI, filename, subcatchments):
    '''
    Modifies the input file dataframe and sets the usage of GI in the different subcatchments

    Inputs
    -----
    area: area to be used in GI per subcatchment. 
    
    typeGI: select between bio-retention cell, green roof & permeable pavement
           - bioretention cell: use BioCell
           - green roof: use GreenRoof
           - permeable pavement: use PerPav
    
    
    filename: swmm input file name as a string in the form of a dataframe
    
    
    subcatchment:


    Note: the use is a porcentage.

    Output
    ------
    Swmm input file modified
    '''
    theinputer=pd.read_csv(filename+'.inp', header=None, skip_blank_lines=False)
    #--------------------------------------------------------------
    
    if typeGI=='BioCell':
        lidstring=f'\tBioCell\t1\t{area}\t1\t0\t1\t0'
    elif typeGI=='GreenRoof':
        lidstring=f'\tGreenRoof\t1\t{area}\t1\t0\t0\t1'
    elif typeGI=='PerPav':
        lidstring=f'\tPerPav\t1\t{area}\t1\t0\t1\t0'

    #Gets the index from where the LID USAGE is
    indGI=theinputer.index[theinputer[0]=='[LID_USAGE]'] 
    locGI=theinputer.index.get_loc(indGI[0])

    df=inputer['subcatchments'].copy()

    gi_info=[]
    for index,row in df.iterrows():
        if row['Name'] in subcatchments:
            if row['Area']>=(area/10000):
                data_string=row['Name']+lidstring
                gi_info.append(data_string)
            else:
                value=row['Area']*10000
                data_string=row['Name']+lidstring
                gi_info.append(data_string)

    data_strings = pd.DataFrame(gi_info)

    #Insert new data
    dfA=theinputer[theinputer.index<= locGI+2]
    dfB=theinputer[theinputer.index>locGI+3]

    theinputermodified=dfA.append(data_strings, ignore_index=True)
    theinputermodified=theinputermodified.append(dfB, ignore_index=True)

    #Index information Subcatchments
    indsub=theinputermodified.index[theinputermodified[0]=='[SUBCATCHMENTS]']
    ind2sub=theinputermodified.index[theinputermodified[0]=='[SUBAREAS]']
    locsub=theinputermodified.index.get_loc(indsub[0])
    loc2sub=theinputermodified.index.get_loc(ind2sub[0])

    #set %impervious as floating number
    df[['%Imperv','Area']] = df[['%Imperv','Area']].astype(float)

    #Change imperviousness
    for index, row in df.iterrows():
        if row['Name'] in subcatchments:
            if row['Area']>=area*1000:
                 if row['%Imperv']>= (100*area(1/10000)*(1/row['Area'])):
                    df.loc[index,'%Imperv']= row['%Imperv']-100*area*(1/10000)*(1/row['Area'])
            else:
                value=row['Area']
                if row['%Imperv']>= (100*value*(1/row['Area'])):
                    df.loc[index,'%Imperv']= row['%Imperv']-100*value*(1/10000)*(1/row['Area'])

    #Data series new rainfall data
    data=df.round(2).astype(str)+'\t'
    data_strings = pd.DataFrame(data.values.sum(axis=1))

    #Insert new data
    dfA=theinputermodified[theinputermodified.index<= locsub+2]
    dfB=theinputermodified[theinputermodified.index>=loc2sub]

    theinputermod=dfA.append(data_strings, ignore_index=True)
    theinputermod=theinputermod.append(dfB, ignore_index=True)

    fin=filename+str(hash(''.join(subcatchments)))+f'area_{area}'+f'{typeGI}'+'.inp'

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
    with Simulation(filename+'.inp') as sim:
        for node in tqdm(Nodes(sim)):
            floodnode[node.nodeid]=st.extract(filename+'.out',['node', node.nodeid, 'Flow_lost_flooding'])
    
    print('Result Extraction Done!')
    
    for key, value in floodnode.items():
        value.rename(columns={'node_{}_Flow_lost_flooding'.format(key):key},inplace=True)
        
    floodrate=pd.DataFrame()
    floodrate['timestamp']=floodnode[list(floodnode.keys())[0]].index
    
    for key, value in tqdm(floodnode.items()):
        floodrate[key]=value[key].values
    
    return floodrate.drop(range(500,floodrate.count()[0]))


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
    area=1000
    typeGI='PerPav'
    
    LIDGIsubcat_area(area,typeGI,filename,i)

    fin=filename+str(hash(''.join(i)))+f'area_{area}'+f'{typeGI}'

    sim=Simulation(fin+'.inp')
    sim.execute()

    res=result_extract(fin)
    print('Result extraction done!')

    os.remove(fin+'.inp')
    os.remove(fin+'.out')
    os.remove(fin+'.rpt')

    print('Files removed!')

    return res

def simulGI_nodes_unpack(args):
    return simulGI_nodes(*args)

def set_simulGI_node(j, rs, num_processors,filename):
    '''
    Input
    ------
    j: simulation number
    rs: random sequence -- each element of the list is a list.
    num_processors: the number of processors to be used - MAX 12
    
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
    print(f'RES Simulation {j} finished at time {elapsed}.')

    return output

def save_results(j,rs,storm,output):
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
    
    for i in range(0, len(output)):
        output[i].to_csv(f'GI_results/simulation_{storm}_{j}_{i}')

        
    rswrite=''

    for i in rs:
        rswrite=rswrite+'\n'+','.join(i)
    f=open(f'GI_results/rs{storm}_{j}','w')
    f.write(rswrite)
    f.close()
    print(f'Results saved for simulation {j}')
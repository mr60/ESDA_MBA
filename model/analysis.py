import pandas as pd
import numpy as np
from tqdm import tqdm

def res_a(df):
    '''
    Calculates resilience inicators for each node
    
    Input
    -----
    df: Pandas dataframe with timeseries results
    
    Output
    ------
     Resilience assessment indicators
     - maxim: failure magnitude
     - duration: failure duration
     - timetostrain: time to strain
     - failurerate: failure rate
     - recoveryrate: recovery rate
     - severity: severity 
    
    '''
    #Returns the index of the last zero
    #Returns the index of the first zero
    
    
    
    m1=df.ne(0).idxmax()
    m2=df.ne(0)[::-1].idxmax()
    
    res=pd.DataFrame(dict(positionstart=m1, start=df.lookup(m1, m1.index),positionend=m2,end=df.lookup(m2, m2.index)))
    
    res.drop(index='timestamp',inplace=True)
                     
    maxim=[]
    duration=[]
    timetostrain=[]
    failurerate=[]
    recoveryrate=[]
    severity=[]
    
    for index,row in res.iterrows():
        if row['start']!=0:
            maxim.append(df[index].max())
            
            duration.append((df.loc[row['positionend'],'timestamp']-df.loc[row['positionstart'],'timestamp']).seconds)
            timetostrain.append((df.loc[df[index].idxmax(),'timestamp']-df.loc[0,'timestamp']).seconds)
            
            
            failuretime=(df.loc[df[index].idxmax(),'timestamp']-df.loc[row['positionstart'],'timestamp']).seconds
            recoverytime=(df.loc[row['positionend'],'timestamp']-df.loc[df[index].idxmax(),'timestamp']).seconds
            
            if failuretime==0:
                failurerate.append(0)
            else:
                failurerate.append(df[index].max()/float(failuretime))
                
            if recoverytime==0:
                recoveryrate.append(0)
            else:
                recoveryrate.append(df[index].max()/float(recoverytime))

            severity.append(np.trapz(df[index]))
            
        else:
            maxim.append(0)
            
            duration.append(0)
            
            timetostrain.append(0)
            
            severity.append(0)

            failurerate.append(0)
            
            recoveryrate.append(0)
            
    
    resilience=pd.DataFrame()
    resilience['Magnitude']=maxim
    resilience['Duration']=duration
    resilience['Time_to_strain']=timetostrain
    resilience['Failure_rate']=failurerate
    resilience['Recovery_rate']=recoveryrate
    resilience['Severity']=severity
    
    return resilience

def res_sys(df):
    '''
    Calculates resilience indicator of the system based on nodes results
    
    Input
    -----
    df: Pandas dataframe with timeseries results
    
    Output
    ------
     Resilience assessment indicators
     - maxim: failure magnitude
     - duration: failure duration
     - timetostrain: time to strain
     - failurerate: failure rate
     - recoveryrate: recovery rate
     - severity: severity 
    
    '''
    res_sys=pd.DataFrame()
    
    res_sys['Magnitude']=[df['Magnitude'].mean(),df['Magnitude'].min(),df['Magnitude'].max()]
    res_sys['Duration']=[df['Duration'].mean(),df['Duration'].min(),df['Duration'].max()]
    res_sys['Time_to_strain']=[df['Time_to_strain'].mean(),df['Time_to_strain'].min(),df['Time_to_strain'].max()]
    res_sys['Failure_rate']=[df['Failure_rate'].mean(),df['Failure_rate'].min(),df['Failure_rate'].max()]
    res_sys['Recovery_rate']=[df['Recovery_rate'].mean(),df['Recovery_rate'].min(),df['Recovery_rate'].max()]
    res_sys['Severity']=[df['Severity'].sum(),df['Time_to_strain'].min(),df['Time_to_strain'].max()]
    
    return res_sys

def cso_wwtp(df1,df2):
    '''
    Calculates CSO & WWTP related indicators
    
    Input
    -----
    df1: Pandas dataframe with CSO timeseries results
    df2: Pandas dataframe with WWTP timeseries results
    
    Output
    ------
    
     CSO indicators
     - maxim: failure magnitude
     - duration: failure duration
     - timetostrain: time to strain
     - severity: total volume CSO
     
     WWTP indicators
     - Total volume WWTP
    
    '''
    m1=df1['node_SX96882104_Total_inflow'].ne(0).idxmax()
    m2=df1['node_SX96882104_Total_inflow'].ne(0)[::-1].idxmax()
    
    cso=pd.DataFrame()
    cso.loc[0,'maxim']=df1['node_SX96882104_Total_inflow'].max()
    cso.loc[0,'duration']=((df1.loc[m2,'timestamp']-df1.loc[m1,'timestamp']).seconds)
    cso.loc[0,'timetostrain']=((df1.loc[df1['node_SX96882104_Total_inflow'].idxmax(),'timestamp']-df1.loc[0,'timestamp']).seconds)
    cso.loc[0,'severity']=np.trapz(df1['node_SX96882104_Total_inflow'])
    
    
    wwtp=pd.DataFrame()
    wwtp.loc[0,'volume']=np.trapz(df2['node_SX94899203_Total_inflow'])
    
    return cso , wwtp


def use_green(typeGI,use,storms):
    '''
    Functions imports data orgininated from the simulations & calculation of indicators
    Inputs
    -----
    typeGI: 'PerPav', 'BioCell', 'GreenRoof'
    
    Outputs
    -------
    use_gi: dictionary with pandas dataframes with results for each node, system, cso & wwtp
    
    '''
    use_gi=dict()

    for j in tqdm(use):
        use_gi[j]=dict()

        for i in tqdm(storms):
            flood=pd.read_csv('results/use/simulation_'+i+'_'+typeGI+'_'+str(j)+'_flood')
            flood['timestamp']=pd.to_datetime(flood['timestamp'])
            resilience=res_a(flood)

            res_system=res_sys(resilience)

            cso_flow=pd.read_csv('results/use/simulation_'+i+'_'+typeGI+'_'+str(j)+'_cso')
            cso_flow['timestamp']=pd.to_datetime(cso_flow['timestamp'])

            wwtp_flow=pd.read_csv('results/use/simulation_'+i+'_'+typeGI+'_'+str(j)+'_wwtp')
            wwtp_flow['timestamp']=pd.to_datetime(wwtp_flow['timestamp'])

            cso,wwtp=cso_wwtp(cso_flow,wwtp_flow)

            use_gi[j][i]=[flood,resilience, res_system, cso, wwtp]
    
    return use_gi

def use_one_green(typeGI,use):
    '''
    Functions imports data orgininated from the simulations & calculation of indicators
    Inputs
    -----
    typeGI: 'PerPav', 'BioCell', 'GreenRoof'
    
    Outputs
    -------
    use_gi: dictionary with pandas dataframes with results for each node, system, cso & wwtp
    
    '''
    use_gi=dict()

    for j in tqdm(use):
        use_gi[j]=dict()

        for i in tqdm(storms):
            use_gi[j][i]=dict()
            
            for n in tqdm(range(0,len(subcat))):
                flood=pd.read_csv('results/one/simulation_'+i+'_use'+str(j)+'_'+typeGI+'_'+str(n)+'_flood')
                flood['timestamp']=pd.to_datetime(flood['timestamp'])
                resilience=res_a(flood)

                res_system=res_sys(resilience)

                cso_flow=pd.read_csv('results/use/simulation_'+i+'_'+typeGI+'_'+str(j)+'_cso')
                cso_flow['timestamp']=pd.to_datetime(cso_flow['timestamp'])

                wwtp_flow=pd.read_csv('results/use/simulation_'+i+'_'+typeGI+'_'+str(j)+'_wwtp')
                wwtp_flow['timestamp']=pd.to_datetime(wwtp_flow['timestamp'])

                cso,wwtp=cso_wwtp(cso_flow,wwtp_flow)

                use_gi[j][i][n]=[flood,resilience, res_system, cso, wwtp]
    
    return use_gi

def sys_resilience(use_gi,use_all):
    '''
    Organising the system resilience in a unique DataFrame
    Input
    -----
    use_gi: dictonary with all the data uploaded from simulations
    Output
    ------
    res_sy_gi: dictionary with dataframes for all the storms & uses
    '''
    
    res_sy_gi=dict()

    for j in use_all:
        res_sy_gi[j]=pd.DataFrame()
        for i in tqdm(storms):
            res_sy_gi[j][i]=use_gi[j][i][2].T[0]
    
        
    return res_sy_gi

def dif_sy(res_sy_gi,use):
    
    res_sy_gi_dif=dict()
    for i in use:
        res_sy_gi_dif[i]=pd.DataFrame()
        res_sy_gi_dif[i]=100*(res_sy_gi[i]-res_sy_gi[0])/res_sy_gi[0]

        res_sy_gi_dif[i]=res_sy_gi_dif[i].T

    indicators=list(res_sy_gi_dif[5].columns)

    dif_indicators_gi=dict()

    for i in indicators:
        dif_indicators_gi[i]=pd.DataFrame()

        for j in use:
            dif_indicators_gi[i][j]=res_sy_gi_dif[j][i]
            
    for j in use:
        res_sy_gi_dif[j]=res_sy_gi_dif[j].reset_index().rename(columns={'index':'Storm'})

        res_sy_gi_dif[j]['Return']=res_sy_gi_dif[j]['Storm'].apply(lambda i: i.split('y')[0][1::])
        res_sy_gi_dif[j]['Return']=res_sy_gi_dif[j]['Return'].astype('int')

        res_sy_gi_dif[j]['Storm_Duration']=res_sy_gi_dif[j]['Storm'].apply(lambda i: i.split('y')[1].split('h')[0].split('m')[0])
        res_sy_gi_dif[j]['Storm_Duration']=res_sy_gi_dif[j]['Storm_Duration'].astype('int')
        res_sy_gi_dif[j]['Storm_Duration']=res_sy_gi_dif[j]['Storm_Duration'].apply(lambda i: 0.5 if i==30 else i)


    for j in indicators:
        dif_indicators_gi[j]=dif_indicators_gi[j].reset_index().rename(columns={'index':'Storm'})

        dif_indicators_gi[j]['Return']=dif_indicators_gi[j]['Storm'].apply(lambda i: i.split('y')[0][1::])
        dif_indicators_gi[j]['Return']=dif_indicators_gi[j]['Return'].astype('int')

        dif_indicators_gi[j]['Storm_Duration']=dif_indicators_gi[j]['Storm'].apply(lambda i: i.split('y')[1].split('h')[0].split('m')[0])
        dif_indicators_gi[j]['Storm_Duration']=dif_indicators_gi[j]['Storm_Duration'].astype('int')
        dif_indicators_gi[j]['Storm_Duration']=dif_indicators_gi[j]['Storm_Duration'].apply(lambda i: 0.5 if i==30 else i)

    
    return res_sy_gi_dif, dif_indicators_gi

def cso(use_gi,use_all):
    cso_BC=dict()

    for j in use_all:
        cso_gi[j]=pd.DataFrame()
        
        for i in tqdm(storms):
            cso_gi[j][i]=use_gi[j][i][3].T[0]
    

        
        return cso_gi
    
def cso_dif(cso_gi,use_all):
    cso_gi_dif=dict()
    
    for i in use:
        cso_gi_dif[i]=pd.DataFrame()
        cso_gi_dif[i]=100*(cso_gi[i]-cso_gi[0])/cso_gi[0]
    
    cso_gi_dif[i]=cso_gi_dif[i].T
    
    indicators=list(cso_gi_dif[5].columns)

    dif_indicators_cso=dict()

    for i in indicators:
        dif_indicators_cso[i]=pd.DataFrame()
    
        for j in use:
            dif_indicators_cso[i][j]=cso_gi_dif[j][i]
            
            
    for j in use:
        cso_BC_dif[j]=cso_BC_dif[j].reset_index().rename(columns={'index':'Storm'})

        cso_BC_dif[j]['Return']=cso_BC_dif[j]['Storm'].apply(lambda i: i.split('y')[0][1::])
        cso_BC_dif[j]['Return']=cso_BC_dif[j]['Return'].astype('int')

        cso_BC_dif[j]['Storm_Duration']=cso_BC_dif[j]['Storm'].apply(lambda i: i.split('y')[1].split('h')[0].split('m')[0])
        cso_BC_dif[j]['Storm_Duration']=cso_BC_dif[j]['Storm_Duration'].astype('int')
        cso_BC_dif[j]['Storm_Duration']=cso_BC_dif[j]['Storm_Duration'].apply(lambda i: 0.5 if i==30 else i)

    
    for j in indicators:
        dif_indicators_cso[j]=dif_indicators_cso[j].reset_index().rename(columns={'index':'Storm'})

        dif_indicators_cso[j]['Return']=dif_indicators_cso[j]['Storm'].apply(lambda i: i.split('y')[0][1::])
        dif_indicators_cso[j]['Return']=dif_indicators_cso[j]['Return'].astype('int')

        dif_indicators_cso[j]['Storm_Duration']=dif_indicators_cso[j]['Storm'].apply(lambda i: i.split('y')[1].split('h')[0].split('m')[0])
        dif_indicators_cso[j]['Storm_Duration']=dif_indicators_cso[j]['Storm_Duration'].astype('int')
        dif_indicators_cso[j]['Storm_Duration']=dif_indicators_cso[j]['Storm_Duration'].apply(lambda i: 0.5 if i==30 else i)

    
    return cso_gi_dif, dif_indicators_cso

def wwtp(use_gi,use_all):
    
    wwtp_gi=dict()
    for j in use_all:
        wwtp_gi[j]=pd.DataFrame()
        for i in tqdm(storms):
            wwtp_gi[j][i]=use_gi[j][i][4].T[0]

       
    return wwtp_gi


def wwtp_dif(wwtp_gi,use):
    
    wwtp_gi_dif=dict()

    for i in use:
        wwtp_gi_dif[i]=pd.DataFrame()
        wwtp_gi_dif[i]=100*(wwtp_gi[i]-wwtp_gi[0])/wwtp_gi[0]
        wwtp_gi_dif[i]=wwtp_gi_dif[i].T

    dif_indicators_wwtp=pd.DataFrame()

    for j in use:
        dif_indicators_wwtp.loc[:,j]=wwtp_gi_dif[j]['volume']

    for j in use:
        wwtp_gi_dif[j]=wwtp_gi_dif[j].reset_index().rename(columns={'index':'Storm'})

        wwtp_gi_dif[j]['Return']=wwtp_gi_dif[j]['Storm'].apply(lambda i: i.split('y')[0][1::])
        wwtp_gi_dif[j]['Return']=wwtp_gi_dif[j]['Return'].astype('int')

        wwtp_gi_dif[j]['Storm_Duration']=wwtp_gi_dif[j]['Storm'].apply(lambda i: i.split('y')[1].split('h')[0].split('m')[0])
        wwtp_gi_dif[j]['Storm_Duration']=wwtp_gi_dif[j]['Storm_Duration'].astype('int')
        wwtp_gi_dif[j]['Storm_Duration']=wwtp_gi_dif[j]['Storm_Duration'].apply(lambda i: 0.5 if i==30 else i)



    dif_indicators_wwtp=dif_indicators_wwtp.reset_index().rename(columns={'index':'Storm'})

    dif_indicators_wwtp['Return']=dif_indicators_wwtp['Storm'].apply(lambda i: i.split('y')[0][1::])
    dif_indicators_wwtp['Return']=dif_indicators_wwtp['Return'].astype('int')

    dif_indicators_wwtp['Storm_Duration']=dif_indicators_wwtp['Storm'].apply(lambda i: i.split('y')[1].split('h')[0].split('m')[0])
    dif_indicators_wwtp['Storm_Duration']=dif_indicators_wwtp['Storm_Duration'].astype('int')
    dif_indicators_wwtp['Storm_Duration']=dif_indicators_wwtp['Storm_Duration'].apply(lambda i: 0.5 if i==30 else i)
    
    return wwtp_gi_dif, dif_indicators_wwtp
    
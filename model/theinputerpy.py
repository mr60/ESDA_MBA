'''

.oooooo..o oooooo   oooooo     oooo ooo        ooooo ooo        ooooo
d8P'    `Y8  `888.    `888.     .8'  `88.       .888' `88.       .888'
Y88bo.        `888.   .8888.   .8'    888b     d'888   888b     d'888
 `"Y8888o.     `888  .8'`888. .8'     8 Y88. .P  888   8 Y88. .P  888
     `"Y88b     `888.8'  `888.8'      8  `888'   888   8  `888'   888
oo     .d8P      `888'    `888'       8    Y     888   8    Y     888
8""88888P'        `8'      `8'       o8o        o888o o8o        o888o


Python tools to interact with the EPA SWMM
Mayra Rodriguez, 2020

CWS, University of Exeter

Modifies SWMM input files depending on uncertainties fixed

'''

#PACKAGE IMPORT
#=======================
import sys, os
import math
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#MODEL SETUP
#=============================
def import_inputfile(filename):

    '''
    Imports the INPUTFILE into a pandas dataframe.

    Inputs
    ------
    filename: filename/path for the input file this must be a text file correctly formatted for SWMM.

    Outputs
    -------
    the input: pandas dataframe of the template file, with one column, and a line for each line of text.
    '''

    theinputer=pd.read_csv(filename, header=None, skip_blank_lines=False)

    return theinputer

#SECTIONS IN THE INPUT FILE
#==================================
def determinesections(theinputer):

    '''
    Based on the swmm input file dataframe, it determines the indexes for the different sections
    Inputs
    ------
    theinputer: the swmm input file dataframe

    Outputs
    -------
    the indexes where the sections are
    '''

    theindexes= theinputer[theinputer['[0]'].str.contains('[',regex=False)]
    theindexes=theindexes.reset_index()
    theindexes=s.rename(columns={'index':'Index','[TITLE]':'Sections'})

    return theindexes

#CHANGE RAINFALL TIMESERIES BASED ON CLIMATE CHANGE FACTOR
#============================================================
def set_rainfall(theinputer, rainfall, ccf=1):

    '''
    Modifies the inputfile dataframe and sets rainfall pattern
    This can be modified using a Climate Change Factor

    Inputs
    ------
    theinputer: swmm input file in the form of a dataframe
    ccf: climate change factor
    rainfall: rainfall dataframes series

    Outputs
    -------
    theinputermodified: swmm input file as dataframe with changed rainfall
    '''

    #change rainfall dataframe based on
    rainfall['Value']=ccf*rainfall['Value']

    #Index information where time series begin and end
    ind=theinputer.index[theinputer[0]=='[TIMESERIES]']
    ind2=theinputer.index[theinputer[0]=='[PATTERNS]']
    loc=theinputer.index.get_loc(ind[0])
    loc2=theinputer.index.get_loc(ind2[0])

    #load entire base model input file
    df= theinputer.iloc[loc+3:loc2]

    #Remove old timeseries
    theinputer=theinputer.drop(list(range(loc+3,loc2)),axis=0)

    #Data series new rainfall data
    data=rainfall.round(6).astype(str)+'\t'
    data_strings = pd.DataFrame(data.values.sum(axis=1))

    #Insert new data
    dfA=theinputer[theinputer.index<= loc+3]
    dfB=theinputer[theinputer.index>loc+3]

    theinputermodified=dfA.append(data_strings, ignore_index=True)
    theinputermodified=theinputermodified.append(dfB, ignore_index=True)

    return theinputermodified

#CHANGE SUBCATCHMENT IMPERVIOUSNESS
#=======================================
def set_sub(theinputer, icf=1):
    '''
    Modifies the input file dataframe and changes imperviousness values/
    The modification occurs by using a imperviousness change factor.

    Inputs
    -------
    theinputer: swmm input file in the form of a dataframe
    icf:changes the imperviousness in the subcatchment

    Outputs
    --------
    theinpuermodified: swmm input file as a dataframe with changed impreviousnes values

    '''
    #Index information Subcatchments#Index information Subcatchments
    ind=theinputer.index[theinputer[0]=='[SUBCATCHMENTS]']
    ind2=theinputer.index[theinputer[0]=='[SUBAREAS]']
    loc=theinputer.index.get_loc(ind[0])
    loc2=theinputer.index.get_loc(ind2[0])

    #gets the index from where the Timeseries start
    ind=theinputer.index[theinputer[0]=='[SUBCATCHMENTS]']

    #gets the index from where the Timeseries end
    ind2=theinputer.index[theinputer[0]=='[SUBAREAS]']

    #gets the interger position TIMESERIES END
    loc=theinputer.index.get_loc(ind[0])

    #gets the interger position TIMESERIES END
    loc2=theinputer.index.get_loc(ind2[0])

    #load entire base model input file
    df= theinputer.iloc[loc+3:loc2-1].copy()
    df.reset_index(drop=True, inplace=True)

    #split into several columns using spaces as delimiters
    df[['Name', 'Raingage', 'Outlet', 'Area','%Imperv','Width','Slope', 'Curblen','SnowPack']] = df[0].str.split('\t',0, expand=True,)

    #drop unneeded columns
    df.drop(columns=[0], inplace=True)

    #set %impervious as floating number
    df['%Imperv'] = df['%Imperv'].astype(float)

    #changes impervious according to factor
    df['%Imperv']= df['%Imperv']*icf

    #re-index from zero
    df.reset_index(drop=True, inplace=True)

    #Remove old timeseries
    theinputer=theinputer.drop(list(range(loc+3,loc2)),axis=0)

    #Data series new rainfall data
    data=df.round(6).astype(str)+'\t'
    data_strings = pd.DataFrame(data.values.sum(axis=1))

    #Insert new data
    dfA=theinputer[theinputer.index<= loc+3]
    dfB=theinputer[theinputer.index>loc+3]

    theinputermodified=dfA.append(data_strings, ignore_index=True)
    theinputermodified=theinputermodified.append(dfB, ignore_index=True)
    return theinputermodified

#CHANGE SUBCATCHMENT AREAS
#=======================================
def set_area(theinputer, imp=1):
    '''
    Modifies the input file dataframe and changes imperviousness values/
    The modification occurs by using a imperviousness change factor.

    Inputs
    -------
    theinputer: swmm input file in the form of a dataframe
    icf:changes the imperviousness in the subcatchment

    Outputs
    --------
    theinpuermodified: swmm input file as a dataframe with changed impreviousnes values

    '''
    #Index information Subcatchments#Index information Subcatchments
    ind=theinputer.index[theinputer[0]=='[SUBCATCHMENTS]']
    ind2=theinputer.index[theinputer[0]=='[SUBAREAS]']
    loc=theinputer.index.get_loc(ind[0])
    loc2=theinputer.index.get_loc(ind2[0])

    #gets the index from where the Timeseries start
    ind=theinputer.index[theinputer[0]=='[SUBCATCHMENTS]']

    #gets the index from where the Timeseries end
    ind2=theinputer.index[theinputer[0]=='[SUBAREAS]']

    #gets the interger position TIMESERIES END
    loc=theinputer.index.get_loc(ind[0])

    #gets the interger position TIMESERIES END
    loc2=theinputer.index.get_loc(ind2[0])

    #load entire base model input file
    df= theinputer.iloc[loc+3:loc2-1].copy()
    df.reset_index(drop=True, inplace=True)

    #split into several columns using spaces as delimiters
    df[['Name', 'Raingage', 'Outlet', 'Area','%Imperv','Width','Slope', 'Curblen','SnowPack']] = df[0].str.split('\t',0, expand=True)

    #drop unneeded columns
    df.drop(columns=[0], inplace=True)

    #set %impervious as floating number
    df['Area'] = df['Area'].astype(float)

    #changes impervious according to factor
    df['Area']= df['Area']*imp

    #re-index from zero
    df.reset_index(drop=True, inplace=True)

    #Remove old timeseries
    theinputer=theinputer.drop(list(range(loc+3,loc2)),axis=0)

    #Data series new rainfall data
    data=df.round(6).astype(str)+'\t'
    data_strings = pd.DataFrame(data.values.sum(axis=1))

    #Insert new data
    dfA=theinputer[theinputer.index<= loc+3]
    dfB=theinputer[theinputer.index>loc+3]

    theinputermodified=dfA.append(data_strings, ignore_index=True)
    theinputermodified=theinputermodified.append(dfB, ignore_index=True)

    return theinputermodified

#CHANGE DWF WITH WATER CONSUMPTION CHANGE FACTOR
#===================================================
def set_dwf(theinputer, watc=1):
    '''
    Modifies the inputfile dataframe and sets rainfall pattern
    This can be modified using a water consumption change factor

    Inputs
    ------
    theinputer: swmm input file in the form of a dataframe
    watc: changes the water consumption

    Outputs
    -------
    theinputermodified: swmm input file as dataframe with changed daily pattern.
    '''

    ind2=theinputer.index[theinputer[0]=='[PATTERNS]'] #gets the index from where the Timeseries end
    loc2=theinputer.index.get_loc(ind2[0]) #gets the interger position TIMESERIES END

    #change DWF due to population change
    base_daily=[1,1,1,1,1,1,1]
    new_daily=[i*watc for i in base_daily]
    nd='\t'.join([str(i) for i in new_daily])
    nd='DAILY_POP_1\tDAILY\t'+nd

    #Insert new data
    theinputer.at[loc2+3]=nd

    return theinputer

#CHANGE DWF WITH WATER CONSUMPTION & POPULATION CHANGE FACTOR
#===================================================
def set_dwf2(theinputer, pop=1,watc=1):
    '''
    Modifies the inputfile dataframe and sets rainfall pattern
    This can be modified using a water consumption change factor

    Inputs
    ------
    theinputer: swmm input file in the form of a dataframe
    watc: changes the water consumption

    Outputs
    -------
    theinputermodified: swmm input file as dataframe with changed daily pattern.
    '''

    ind2=theinputer.index[theinputer[0]=='[PATTERNS]'] #gets the index from where the Timeseries
    loc2=theinputer.index.get_loc(ind2[0]) #gets the interger position TIMESERIES

    #change DWF due to population change
    base_daily=[1,1,1,1,1,1,1]
    new_daily=[i*watc*pop for i in base_daily]
    nd='\t'.join([str(i) for i in new_daily])
    nd='DAILY_POP_1\tDAILY\t'+nd

    #Insert new data
    theinputer.at[loc2+3]=nd

    return theinputer

#CHANGE USE OF GI
#=======================
def set_useGI(theinputer, use=0):
    '''
    Modifies the input file dataframe and sets the usage of GI in the different subcatchments

    Inputs
    -----
    theinputer: swmm input file in the form of a dataframe
    use: change the GI implementation in the different subcatchments

    Note: the use is a porcentage.

    Output
    ------
    theinputermodified: swmm input file as dataframe with changed daily pattern
    '''

    if use==0:
        theinputermodified=theinputer
    else:
        #GETS THE NAMES OF SUBCATCHMENTS & AREAS
        #------------------------------------------
        #Index information Subcatchments#Index information Subcatchments
        ind=theinputer.index[theinputer[0]=='[SUBCATCHMENTS]']
        ind2=theinputer.index[theinputer[0]=='[SUBAREAS]']
        loc=theinputer.index.get_loc(ind[0])
        loc2=theinputer.index.get_loc(ind2[0])

        #gets the index from where the Timeseries start
        ind=theinputer.index[theinputer[0]=='[SUBCATCHMENTS]']

        #gets the index from where the Timeseries end
        ind2=theinputer.index[theinputer[0]=='[SUBAREAS]']

        #gets the interger position TIMESERIES END
        loc=theinputer.index.get_loc(ind[0])

        #gets the interger position TIMESERIES END
        loc2=theinputer.index.get_loc(ind2[0])

        #load entire base model input file
        df= theinputer.iloc[loc+3:loc2-1].copy()
        df.reset_index(drop=True, inplace=True)

        #split into several columns using spaces as delimiters
        df[['Name', 'Raingage', 'Outlet', 'Area','%Imperv','Width','Slope', 'Curblen','SnowPack']] = df[0].str.split('\t',0, expand=True,)

        #GETS THE LID USAGE INDEX & SETS THE USAGE IN THE INPUT FILE
        #--------------------------------------------------------------
        #Gets the index from where the LID USAGE is
        indGI=theinputer.index[theinputer[0]=='[LID_USAGE]']
        locGI=theinputer.index.get_loc(indGI[0])

        #Changes the dataframe with subacatchment to match the LID USAGE format
        #drop unneeded columns
        df.drop(columns=[0,'Raingage','Outlet','%Imperv','Slope','Curblen','SnowPack'], inplace=True)

        #Inserts columns to be complient with the LID_USAGE format in the input file
        #LID Name column
        lidname=['GreenRoof']*df.shape[0]
        df.insert(1, 'LID', lidname, True)

        #LID Number
        numbers=[1]*df.shape[0]
        df.insert(2, 'Number', numbers, True)

        #LID initSat -- sets the initial saturation as 0, this can be changed
        sat=[0]*df.shape[0]
        df.insert(5,'IniSat',sat, True)

        #LID FromImp -- if set 0 it means that it only treats the rain that it gets. This can also be changed
        imp=[0]*df.shape[0]
        df.insert(6,'FromImp',imp,True)

        #LID ToPerv -- if set 0 this means that flow doesnt get routed to pervious area. This can be changed
        toperv=[0]*df.shape[0]
        df.insert(7,'ToPerv',toperv,True)

        #Sets the LID Area based on the original Subcatchment area and USE porcentage
        df['Area'] = df.Area.astype(float)
        df['Area']=use*10000*df['Area']

        #sets the LID Width based on the original Subcatchment Width and USE Porcentage
        df['Width'] = df.Width.astype(float)
        df['Width']=use*df['Width']

        #Data series new LID_USAGE data
        data=df.round(6).astype(str)+'\t'
        data_strings = pd.DataFrame(data.values.sum(axis=1))

        #Insert new data
        dfA=theinputer[theinputer.index<= locGI+2]
        dfB=theinputer[theinputer.index>locGI+3]

        theinputermodified=dfA.append(data_strings, ignore_index=True)
        theinputermodified=theinputermodified.append(dfB, ignore_index=True)

    return theinputermodified

#WRITE INPUT FILE TO USE IN SIMULATION IN SWMM
#===================================================
def write_input(filename, theinputer):
    '''
    Based on a dataframe with data modified it creates a SWMM input file in the correct format

    Inputs
    ------
    filename: it has to be in the form of a string, and has to have .inp at the end
    theinputer: dataframe with the swmm input file

    Output
    ------
    A SWMM input file
    '''

    theinputer.to_csv(filename,header=False, index=False, quoting=3, sep='\n', na_rep=' ')


#GET THE CSO & WTP VOLUME FROM REPORT
#========================================

def get_volume(filename,towtp,out):
    '''
    This functions extracts relevant information from the report file

    *wtp: water treatment plant

    Inputs
    ------
    filename: path to the report file - as a string
    towtp: name of the outfall that goes to the WTP - as a string
    out: name of the outfall node to river/water way - as a string


    Outputs
    -------
    wtpvolume: total volume in 10^6 to wtp
    wtptss: total TSS to wtp
    wtptn: total TN to wtp
    wtptp: total TP to wtp
    wtpcod: total COD to wtp

    Same structure with cso - csovolume, etc.

    Volume Unit 10^6 l
    Contaminants kg
    '''

    #Upload the report
    thereport=pd.read_table(filename,sep='\n',header=None)

    #Where the info is
    ind=thereport.index[thereport[0].str.contains("Outfall Loading Summary",regex=False)]
    loc=thereport.index.get_loc(ind[0])

    #Where the info ends
    ind2=thereport.index[thereport[0].str.contains("Link Flow Summary",regex=False)]
    loc2=thereport.index.get_loc(ind2[0])

    #load entire base model input file
    df= thereport.iloc[loc+7:loc2-1].copy()

    #drop uneeded rows
    df.drop(df[df[0].str.contains('-',regex=False)].index, axis=0, inplace=True)
    df.reset_index(drop=True, inplace=True)

    #format of the df is not good, need to change it
    for i in range(0,df.shape[0]):
        listi=df[0][i].split(' ')
        listi=[x for x in listi if x != '']
        listi='\t'.join(listi)
        df[0][i]=listi

    #split into several columns using spaces as delimiters
    df[['Name', 'FlowFreq', 'AveFlow', 'MaxFlow','TotalV','TotalTSS','TotalTP', 'TotalTN','TotalCOD']] =df[0].str.split('\t',0, expand=True)

    #drop uneeded columns
    df.drop(columns=[0],inplace=True)

    #TO WTP
    wtpvolume=round(float(df[df['Name']==towtp]['TotalV'][df[df['Name']==towtp].index]),1)
    #wtptss=round(float(df[df['Name']==towtp]['TotalTSS'][df[df['Name']==towtp].index]),1)
    #wtptn=round(float(df[df['Name']==towtp]['TotalTN'][df[df['Name']==towtp].index]),1)
    #wtptp=round(float(df[df['Name']==towtp]['TotalTP'][df[df['Name']==towtp].index]),1)
    #wtpcod=round(float(df[df['Name']==towtp]['TotalCOD'][df[df['Name']==towtp].index]),1)

    #CSO
    csovolume=round(float(df[df['Name']==out]['TotalV'][df[df['Name']==out].index]),1)
    #csotss=round(float(df[df['Name']==out]['TotalTSS'][df[df['Name']==out].index]),1)
    #csotn=round(float(df[df['Name']==out]['TotalTN'][df[df['Name']==out].index]),1)
    #csotp=round(float(df[df['Name']==out]['TotalTP'][df[df['Name']==out].index]),1)
    #csocod=round(float(df[df['Name']==out]['TotalCOD'][df[df['Name']==out].index]),1)

    return wtpvolume, csovolume

#GET THE INDICATORS NEEDED FROM REPORT
#========================================

def get_quality(filename,towtp,out):
    '''
    This functions extracts relevant information from the report file

    *wtp: water treatment plant

    Inputs
    ------
    filename: path to the report file - as a string
    towtp: name of the outfall that goes to the WTP - as a string
    out: name of the outfall node to river/water way - as a string


    Outputs
    -------
    wtpvolume: total volume in 10^6 to wtp
    wtptss: total TSS to wtp
    wtptn: total TN to wtp
    wtptp: total TP to wtp
    wtpcod: total COD to wtp

    Same structure with cso - csovolume, etc.

    Volume Unit 10^6 l
    Contaminants kg
    '''

    #Upload the report
    thereport=pd.read_table(filename,sep='\n',header=None)

    #Where the info is
    ind=thereport.index[thereport[0].str.contains("Outfall Loading Summary",regex=False)]
    loc=thereport.index.get_loc(ind[0])

    #Where the info ends
    ind2=thereport.index[thereport[0].str.contains("Link Flow Summary",regex=False)]
    loc2=thereport.index.get_loc(ind2[0])

    #load entire base model input file
    df= thereport.iloc[loc+7:loc2-1].copy()

    #drop uneeded rows
    df.drop(df[df[0].str.contains('-',regex=False)].index, axis=0, inplace=True)
    df.reset_index(drop=True, inplace=True)

    #format of the df is not good, need to change it
    for i in range(0,df.shape[0]):
        listi=df[0][i].split(' ')
        listi=[x for x in listi if x != '']
        listi='\t'.join(listi)
        df[0][i]=listi

    #split into several columns using spaces as delimiters
    df[['Name', 'FlowFreq', 'AveFlow', 'MaxFlow','TotalV','TotalTSS','TotalTP', 'TotalTN','TotalCOD']] =df[0].str.split('\t',0, expand=True)

    #drop uneeded columns
    df.drop(columns=[0],inplace=True)

    #TO WTP
    #wtpvolume=round(float(df[df['Name']==towtp]['TotalV'][df[df['Name']==towtp].index]),1)
    wtptss=round(float(df[df['Name']==towtp]['TotalTSS'][df[df['Name']==towtp].index]),1)
    wtptn=round(float(df[df['Name']==towtp]['TotalTN'][df[df['Name']==towtp].index]),1)
    wtptp=round(float(df[df['Name']==towtp]['TotalTP'][df[df['Name']==towtp].index]),1)
    #wtpcod=round(float(df[df['Name']==towtp]['TotalCOD'][df[df['Name']==towtp].index]),1)

    #CSO
    #csovolume=round(float(df[df['Name']==out]['TotalV'][df[df['Name']==out].index]),1)
    csotss=round(float(df[df['Name']==out]['TotalTSS'][df[df['Name']==out].index]),1)
    csotn=round(float(df[df['Name']==out]['TotalTN'][df[df['Name']==out].index]),1)
    csotp=round(float(df[df['Name']==out]['TotalTP'][df[df['Name']==out].index]),1)
    #csocod=round(float(df[df['Name']==out]['TotalCOD'][df[df['Name']==out].index]),1)

    return wtptss,wtptn, wtptp, csotss, csotn, csotp

#GETS THE TOTAL RUNOFF VOLUME
#=================================
def get_runoff(filename,use):

    '''
    This functions extracts relevant information from the report file


    Inputs
    ------
    filename: path to the report file - as a string

    Outputs
    -------
    vrunoff: total volume runoff

    Volume Unit 10^6 L
    '''

    if use==0:
        #Upload the report
        thereport=pd.read_table(filename,sep='\n',header=None)

        #Where the info is TOTAL V RUNOFF
        indr=thereport.index[thereport[0].str.contains("Subcatchment Runoff Summary",regex=False)]
        locr=thereport.index.get_loc(indr[0])

        #Where the info ends
        indr2=thereport.index[thereport[0].str.contains("Subcatchment Washoff Summary",regex=False)]
        locr2=thereport.index.get_loc(indr2[0])

        #load entire base model input file
        df= thereport.iloc[locr+7:locr2-1].copy()

        #drop uneeded rows
        df.drop(df[df[0].str.contains('-',regex=False)].index, axis=0, inplace=True)
        df.reset_index(drop=True, inplace=True)

        #format of the df is not good, need to change it
        for i in range(0,df.shape[0]):
            listi=df[0][i].split(' ')
            listi=[x for x in listi if x != '']
            listi='\t'.join(listi)
            df[0][i]=listi

        #split into several columns using spaces as delimiters
        df[['Subcatchment', 'TotalPrec','TotalRunon', 'TotalEv', 'TotalInf','ImpvRunoff','PervRunoff','TotalRunoff','TotalVRunoff', 'PeakRunoff','RunoffCoeff']] =df[0].str.split('\t',0, expand=True)

        #drop uneeded columns
        df.drop(columns=[0],inplace=True)

        #Calculate total runoff
        df.TotalVRunoff=df.TotalVRunoff.astype(float)
        vrunoff=round(df.TotalVRunoff.sum(),1)
    else:
        #Upload the report
        thereport=pd.read_table(filename,sep='\n',header=None)

        #Where the info is TOTAL V RUNOFF
        indr=thereport.index[thereport[0].str.contains("Subcatchment Runoff Summary",regex=False)]
        locr=thereport.index.get_loc(indr[0])

        #Where the info ends
        indr2=thereport.index[thereport[0].str.contains("LID Performance Summary",regex=False)]
        locr2=thereport.index.get_loc(indr2[0])

        #load entire base model input file
        df= thereport.iloc[locr+7:locr2-1].copy()

        #drop uneeded rows
        df.drop(df[df[0].str.contains('-',regex=False)].index, axis=0, inplace=True)
        df.reset_index(drop=True, inplace=True)

        #format of the df is not good, need to change it
        for i in range(0,df.shape[0]):
            listi=df[0][i].split(' ')
            listi=[x for x in listi if x != '']
            listi='\t'.join(listi)
            df[0][i]=listi

        #split into several columns using spaces as delimiters
        df[['Subcatchment', 'TotalPrec','TotalRunon', 'TotalEv', 'TotalInf','ImpvRunoff','PervRunoff','TotalRunoff','TotalVRunoff', 'PeakRunoff','RunoffCoeff']] =df[0].str.split('\t',0, expand=True)

        #drop uneeded columns
        df.drop(columns=[0],inplace=True)

        #Calculate total runoff
        df.TotalVRunoff=df.TotalVRunoff.astype(float)
        vrunoff=round(df.TotalVRunoff.sum(),1)


    return vrunoff

#GETS THE TOTAL FLOOD VOLUME
#==============================

def get_flood(filename):

    '''
    This functions extracts relevant information from the report file


    Inputs
    ------
    filename: path to the report file - as a string

    Outputs
    -------
    vflood: total volume flooding

    Volume Unit 10^6 L
    '''

    #Upload the report
    thereport=pd.read_table(filename,sep='\n',header=None)

    #Where the info is TOTAL V FLOODING
    indr=thereport.index[thereport[0].str.contains("Node Flooding Summary",regex=False)]
    locr=thereport.index.get_loc(indr[0])

    #Where the info ends
    indr2=thereport.index[thereport[0].str.contains("Storage Volume Summary",regex=False)]
    locr2=thereport.index.get_loc(indr2[0])

    #load entire base model input file
    df= thereport.iloc[locr+9:locr2-1].copy()

    #drop uneeded rows
    df.drop(df[df[0].str.contains('-',regex=False)].index, axis=0, inplace=True)
    df.reset_index(drop=True, inplace=True)

    #format of the df is not good, need to change it
    for i in range(0,df.shape[0]):
        listi=df[0][i].split(' ')
        listi=[x for x in listi if x != '']
        listi='\t'.join(listi)
        df[0][i]=listi

    #split into several columns using spaces as delimiters
    df[['Node', 'HoursFlooded','TimeOcc','MaxRate', 'TimeMax', 'TotalVFlood','MaxPonded']] =df[0].str.split('\t',0, expand=True)

    #drop uneeded columns
    df.drop(columns=[0],inplace=True)

    #Calculate total runoff
    df.TotalVFlood=df.TotalVFlood.astype(float)
    vflood=round(df.TotalVFlood.sum(),1)

    return vflood


def setraingage(theinputer,rainfallname):

    ind=theinputer.index[theinputer[0]=='[RAINGAGES]'] 
    loc=theinputer.index.get_loc(ind[0])  

    ind2=theinputer.index[theinputer[0]=='[SUBCATCHMENTS]'] 
    loc2=theinputer.index.get_loc(ind2[0]) 

    #load entire base model input file
    newstorm='1\tVOLUME\t00:01\t1\tTIMESERIES\t' + rainfallname
    theinputer.loc[loc+2,0]=newstorm

    #Insert new data
    dfA=theinputer[theinputer.index<= loc+2]
    dfB=theinputer[theinputer.index>loc2-1]

    theinputermodified=dfA
    theinputermodified=theinputermodified.append(dfB, ignore_index=True)
    
    return theinputermodified
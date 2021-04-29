'''

                                                        r                
                                                       ain
                                                       rai
                                                      nrain
                                                     rainrai
                                                    nrainrain
                                                   ainrainrain
                                                  rainrainrainr
                                                 ainrainrainrain
                                                rainrainrainrainr
                                              ainrainrainrainrainra
                                            inra nrainrainrainrainrai
                                          nrain  inrainrainrainrainrain
                                         rain   nrainrainrainrainrainrai
                                        nrai   inrainrainrainrainrainrain
                                        rai   inrainrainrainrainrainrainr
                                        rain   nrainrainrainrainrainrainr
                                         rainr  nrainrainrainrainrainrai
                                          nrain ainrainrainrainrainrain
                                            rainrainrainrainrainrainr
                                              rainranirainrainrainr
                                                   ainrainrain
                                                   
                                                       SWMM

University of EXETER, 2020
Mayra Rodriguez

This script allows the identification of the main sections in a given SWMM input file. This allows an easy extraction and access of all the information contained in the input file for use in Python. 

The first function imports the input file into a Pandas' Data Frame. 

The second's function output is a python's Dictionary, where the keys are the name of the section and the values are Pandas' Data Frames. 

IMPORTANT NOTE!
---------------
As sometimes the columns are not filled, this may cause problems with importing the file. If you have errors, please check in the sections, if there is an incongruence with the columns and what is written in the code. 

'''

#IMPORT PACKAGES
#========================
import pandas as pd


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


def deteriminesections(df):
    
    '''
    SWMM input into Python - As dataframe
    
    Input
    -----
    Swmm file as a pandas dataframe
    
    Output
    ------
    Dictionary containing all the sections of the input file
    
    '''
   
    
    #Deterimines the indexes for the different sections
    theindexes= df[df[0].str.contains('[',regex=False)==True].copy()
    ind=theindexes.to_dict()
    ind=ind[0]
    ind= {value:key for key, value in ind.items()}
    
    #Create a Dataframe for each section of the input file
    inputer={}
    indexes=list(ind.values())
    sections=list(ind.keys())

    #Create a Dataframe for each section of the input file
    inputer={}
    for i in range(0,len(indexes)-1):
        inputer[sections[i][1:-1].casefold()]=df[indexes[i]+1:indexes[i+1]-1].copy().reset_index(drop=True).rename(columns={0:sections[i][1:-1].casefold()})

    #Raingages
    inputer['raingages'][['Name','Format','Interval','SCF','Source','Tseries']]= inputer['raingages']['raingages'].str.split('\t',0, expand=True)
    inputer['raingages'].drop(columns=['raingages'],index=[0,1],inplace=True)
    inputer['raingages'].reset_index(drop=True,inplace=True)

    #SUBCATCHMENTS
    #=============
    inputer['subcatchments'][['Name', 'Raingage', 'Outlet', 'Area','%Imperv','Width','Slope', 'Curblen','SnowPack']] = inputer['subcatchments']['subcatchments'].str.split('\t',0, expand=True)
    inputer['subcatchments'].drop(columns=['subcatchments'],index=[0,1],inplace=True)
    inputer['subcatchments'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type, so that they can be managed easily
    inputer['subcatchments'][['Area','%Imperv','Width','Slope']]=inputer['subcatchments'][['Area','%Imperv','Width','Slope']].astype('float')

    #SUBAREAS
    #========
    inputer['subareas'][['Name','N-Imperv','N-Perv','S-Imperv','S-Perv','PctZero','RouteTo','PctRouted']]=inputer['subareas']['subareas'].str.split('\t',0, expand=True)
    inputer['subareas'].drop(columns=['subareas'],index=[0,1],inplace=True)
    inputer['subareas'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['subareas'][['N-Imperv','N-Perv','S-Imperv','S-Perv','PctZero']]=inputer['subareas'][['N-Imperv','N-Perv','S-Imperv','S-Perv','PctZero']].astype(float)

    #INFILTRATION
    #============
    inputer['infiltration'][['Name','MaxRate','MinRate','Decay','DryTime','MaxInfil']]=inputer['infiltration']['infiltration'].str.split('\t',0, expand=True)
    inputer['infiltration'].drop(columns=['infiltration'],index=[0,1],inplace=True)
    inputer['infiltration'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['infiltration'][['MaxRate','MinRate','Decay','DryTime','MaxInfil']]=inputer['infiltration'][['MaxRate','MinRate','Decay','DryTime','MaxInfil']].astype(float)

    #LID_USAGE
    #==========
    inputer['lid_usage'][['Name','LIDProcess','Number','Area','Width','InitSat','FromImp','ToPerv','RptFile','DrainTo','FromPerv']]=inputer['lid_usage']['lid_usage'].str.split('\t',0, expand=True)
    inputer['lid_usage'].drop(columns=['lid_usage'],index=[0,1],inplace=True)
    inputer['lid_usage'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['lid_usage'][['Number','Area','Width','InitSat','FromImp','ToPerv','RptFile','DrainTo','FromPerv']]=inputer['lid_usage'][['Number','Area','Width','InitSat','FromImp','ToPerv','RptFile','DrainTo','FromPerv']].astype(float)

    #JUNCTIONS
    #==========
    inputer['junctions'][['Name', 'Elevation', 'MaxDepth', 'InitDepth', 'SurDepth', 'Aponded']]=inputer['junctions']['junctions'].str.split('\t',0, expand=True)
    inputer['junctions'].drop(columns=['junctions'],index=[0,1],inplace=True)
    inputer['junctions'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['junctions'][['Elevation','MaxDepth','InitDepth','SurDepth','Aponded']]=inputer['junctions'][['Elevation','MaxDepth','InitDepth','SurDepth','Aponded']].astype(float)

    #OUTFALLS
    #========
    inputer['outfalls'][['Name', 'Elevation', 'Type', 'StageData', 'Gated', 'RouteTo']]=inputer['outfalls']['outfalls'].str.split('\t',0, expand=True)
    inputer['outfalls'].drop(columns=['outfalls'],index=[0,1],inplace=True)
    inputer['outfalls'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['outfalls'][['Elevation']]=inputer['outfalls'][['Elevation']].astype(float)

    #STORAGE
    #========
    inputer['storage'][['Name','Elevation','MaxDepth','InitDepth','Shape','Curve','Apond','Fevap','Psi','Ksat','IMD']]=inputer['storage']['storage'].str.split('\t',0, expand=True)
    inputer['storage'].drop(columns=['storage'],index=[0,1],inplace=True)
    inputer['storage'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['storage'][['Elevation','MaxDepth','InitDepth','Apond','Fevap']]=inputer['storage'][['Elevation','MaxDepth','InitDepth','Apond','Fevap']].astype(float)

    #CONDUITS
    #==========
    #Drop the annoying comment in the dataframe
    theannoyingcomment=inputer['conduits'][inputer['conduits']['conduits'].str.contains(';\tks\tvalue',regex=False)==True].copy()
    ind=theannoyingcomment.to_dict()
    ind=ind['conduits']
    ind=list(ind.keys())
    inputer['conduits'].drop(index=ind,inplace=True)

    #CONDUIT
    #========
    inputer['conduits'][['Name','NodeFrom','NodeTo','Length','Roughness','InOffset','OutOffset','InitFlow','MaxFlow']]=inputer['conduits']['conduits'].str.split('\t',0, expand=True)
    inputer['conduits'].drop(columns=['conduits'],index=[0,1],inplace=True)
    inputer['conduits'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['conduits'][['Length','Roughness','InOffset','OutOffset','InitFlow','MaxFlow']]=inputer['conduits'][['Length','Roughness','InOffset','OutOffset','InitFlow','MaxFlow']].astype(float)

    #PUMPS
    #=====
    inputer['pumps'][['Name','FromNode', 'NodeTo','PumpCurve', 'Status','Sartup', 'Shutoff']]=inputer['pumps']['pumps'].str.split('\t',0, expand=True)
    inputer['pumps'].drop(columns=['pumps'],index=[0,1],inplace=True)
    inputer['pumps'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['pumps'][['Sartup','Shutoff']]=inputer['pumps'][['Sartup','Shutoff']].astype(float)

    #WEIRS
    #=====
    inputer['weirs'].drop(index=[0,1],inplace=True)
    inputer['weirs'][['Name','FromNode','ToNode','Type', 'CrestHt','Qcoeff','Gated', 'EndCon', 'EndCoeff', 'Surcharge']]=inputer['weirs']['weirs'].str.split('\t',0, expand=True)
    inputer['weirs'].drop(columns=['weirs'],inplace=True)
    inputer['weirs'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['weirs'][['CrestHt','Qcoeff','EndCon','EndCoeff']]=inputer['weirs'][['CrestHt','Qcoeff','EndCon','EndCoeff']].astype(float)

    #XSECTIONS
    #=========
    inputer['xsections'][['Link', 'Shape', 'Geom1', 'Geom2', 'Geom3', 'Geom4', 'Barrels', 'Culvert']]=inputer['xsections']['xsections'].str.split('\t',0, expand=True)
    inputer['xsections'].drop(columns=['xsections'],index=[0,1],inplace=True)
    inputer['xsections'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['xsections'][['Geom1','Geom2','Geom3','Geom4','Barrels']]=inputer['xsections'][['Geom1','Geom2','Geom3','Geom4','Barrels']].astype(float)

    #LOSSES
    #======
    inputer['losses'][['Link', 'Kentry', 'Kexit', 'Kavg', 'FlapGate', 'Seepage']]=inputer['losses']['losses'].str.split('\t',0, expand=True)
    inputer['losses'].drop(columns=['losses'],index=[0,1],inplace=True)
    inputer['losses'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['losses'][['Kentry','Kexit','Kavg','Seepage']]=inputer['losses'][['Kentry','Kexit','Kavg','Seepage']].astype(float)


    #POLLUTANTS
    #============
    inputer['pollutants'][['Name', 'Units', 'Crain', 'Cgw', 'Crdii', 'Kdecay', 'SnowOnly', 'Co-Pollutant', 'Co-Frac', 'Cdwf', 'Cinit']]=inputer['pollutants']['pollutants'].str.split('\t',0, expand=True)
    inputer['pollutants'].drop(columns=['pollutants'],index=[0,1],inplace=True)
    inputer['pollutants'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['pollutants'][['Crain','Cgw','Crdii','Kdecay','Co-Frac','Cdwf','Cinit']]=inputer['pollutants'][['Crain','Cgw','Crdii','Kdecay','Co-Frac','Cdwf','Cinit']].astype(float)

    #LAND USES
    #============
    inputer['landuses'][['Name', 'Sweeping', 'Fraction', 'Last']]=inputer['landuses']['landuses'].str.split('\t',0, expand=True)
    inputer['landuses'].drop(columns=['landuses'],index=[0,1,2],inplace=True)
    inputer['landuses'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['landuses'][['Sweeping','Fraction','Last']]=inputer['landuses'][['Sweeping','Fraction','Last']].astype(float)

    #COVERAGES
    #============
    #ATTENTION: if I add more land uses, more columns must me added or just more lines with different coverages
    inputer['coverages'][['Subcatchment', 'LandUse', 'Percent']]=inputer['coverages']['coverages'].str.split('\t',0, expand=True)
    inputer['coverages'].drop(columns=['coverages'],index=[0,1,2],inplace=True)
    inputer['coverages'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['coverages']['Percent']=inputer['coverages']['Percent'].astype(float)

    #LOADINGS
    #============
    #ATTENTION:if pollutants change, more columns must me added or just more lines with different coverages
    inputer['loadings'][['Subcatchment', 'Pollutant', 'Buildup']]=inputer['loadings']['loadings'].str.split('\t',0, expand=True)
    inputer['loadings'].drop(columns=['loadings'],index=[0,1],inplace=True)
    inputer['loadings'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['loadings']['Buildup']=inputer['loadings']['Buildup'].astype(float)

    #BUILDUP
    #========
    inputer['buildup'][['LandUse', 'Pollutant', 'Function', 'Coeff1', 'Coeff2', 'Coeff3', 'PerUnit']]=inputer['buildup']['buildup'].str.split('\t',0, expand=True)
    inputer['buildup'].drop(columns=['buildup'],index=[0,1],inplace=True)
    inputer['buildup'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['buildup'][['Coeff1','Coeff2','Coeff3']]=inputer['buildup'][['Coeff1','Coeff2','Coeff3']].astype(float)

    #WASHOFF
    #========
    inputer['washoff'][['LandUse', 'Pollutant', 'Function', 'Coeff1', 'Coeff2', 'SweepRmvl', 'BmpRmvl']]=inputer['washoff']['washoff'].str.split('\t',0, expand=True)
    inputer['washoff'].drop(columns=['washoff'],index=[0,1],inplace=True)
    inputer['washoff'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['washoff'][['Coeff1','Coeff2','SweepRmvl','BmpRmvl']]=inputer['washoff'][['Coeff1','Coeff2','SweepRmvl','BmpRmvl']].astype(float)

    #DWF
    #====
    inputer['dwf'][['Node', 'Constituent', 'Baseline', 'Patterns1','Patterns2','Patterns3','Patterns4']]=inputer['dwf']['dwf'].str.split('\t',0, expand=True)
    inputer['dwf'].drop(columns=['dwf'],index=[0,1],inplace=True)
    inputer['dwf'].reset_index(drop=True,inplace=True)

    #Modifying the numeric columns into float type
    inputer['dwf']['Baseline']=inputer['dwf']['Baseline'].astype(float)

    #CURVES
    #======
    inputer['curves'][['Name', 'Type', 'X-Value', 'Y-Value']]=inputer['curves']['curves'].str.split('\t',0, expand=True)
    inputer['curves'].drop(columns=['curves'],index=[0,1],inplace=True)
    inputer['curves'].reset_index(drop=True,inplace=True)

    #Dropping strange rows with ;None 
    theannoyingcomment=inputer['curves'][inputer['curves']['Name'].str.contains(';',regex=False)==True].copy()
    ind=theannoyingcomment.to_dict()
    ind=ind['Name']
    ind=list(ind.keys())
    inputer['curves'].drop(index=ind,inplace=True)

    #Modifying the numeric columns into float type
    inputer['curves'][['X-Value','Y-Value']]=inputer['curves'][['X-Value','Y-Value']].astype(float)

   #TIMESERIES
    #=========
    inputer['timeseries'][['Name', 'Date', 'Time', 'Value']]=inputer['timeseries']['timeseries'].str.split('\t',0, expand=True)
    inputer['timeseries'].drop(columns=['timeseries'],index=[0,1],inplace=True)
    inputer['timeseries'].reset_index(drop=True,inplace=True)

    #Eliminate Test timeseries
    theannoyingcomment=inputer['timeseries'][inputer['timeseries']['Name'].str.contains('Test',regex=False)==True].copy()
    ind=theannoyingcomment.to_dict()
    ind=ind['Name']
    ind=list(ind.keys())
    inputer['timeseries'].drop(index=ind,inplace=True)

    #Drop the ; rows
    theannoyingcomment=inputer['timeseries'][inputer['timeseries']['Name'].str.contains(';',regex=False)==True].copy()
    ind=theannoyingcomment.to_dict()
    ind=ind['Name']
    ind=list(ind.keys())
    inputer['timeseries'].drop(index=ind,inplace=True)

    #Change the index
    inputer['timeseries'].reset_index(drop=True,inplace=True)

    #Modify the columns to the correct datatype
    inputer['timeseries']['Date']=pd.to_datetime(inputer['timeseries']['Date'],dayfirst=False,yearfirst=False,)

    #Modify the columns to correct datatype
    inputer['timeseries']['Time']= [x + ':00' for x in inputer['timeseries']['Time']]
    inputer['timeseries']['Time']=pd.to_timedelta(inputer['timeseries']['Time'])

    #Modify the columns to correct datatype
    inputer['timeseries']['Value']=inputer['timeseries']['Value'].astype(float)

    #COORDINATES
    #=========
    inputer['coordinates'][['Node', 'X', 'Y']]=inputer['coordinates']['coordinates'].str.split('\t',0, expand=True)
    inputer['coordinates'].drop(columns=['coordinates'],index=[0,1],inplace=True)
    inputer['coordinates'].reset_index(drop=True,inplace=True)

    #Modify the columns to correct datatype
    inputer['coordinates'][['X','Y']]=inputer['coordinates'][['X','Y']].astype(float)

    #POLYGONS
    #=========
    inputer['polygons'][['Subcatchment', 'X', 'Y']]=inputer['polygons']['polygons'].str.split('\t',0, expand=True)
    inputer['polygons'].drop(columns=['polygons'],index=[0,1],inplace=True)
    inputer['polygons'].reset_index(drop=True,inplace=True)

    #Modify the columns to correct datatype
    inputer['polygons'][['X','Y']]=inputer['polygons'][['X','Y']].astype(float)

    return inputer



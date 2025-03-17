import pandas as pd
import kagglehub as kh
import os
import glob
import re
from datetime import datetime

dataset_path = "willianoliveiragibin/grocery-inventory"
proj = 'grocery'

def download_dataset(dataset_path,path=''):
    '''
    Download dataset.
    Example
    path = kh.dataset_download(ecomm_dataset_path)
    print("Path to dataset files:", path)
    '''
    return kh.dataset_download(dataset_path,path=path)

def read_dataset(path):
    '''
    Return DataFrame from path
    '''
    _,ext = os.path.splitext(path)
    if ext == '.csv':
        return pd.read_csv(path)
    elif ext == '.xlsx':
        return pd.read_excel(path)
    elif ext == '.json':
        return pd.read_json(path)
    return pd.DataFrame
def get_dataset():
    '''
    Get dataset : dataset_path
    '''
    path = download_dataset(dataset_path)
    globs = [g for g in glob.iglob(os.path.join(path,f'{proj}*')) if not g.endswith('.py')]
    return globs[0]

def dataset_to_frame(path):
    '''
    Create DataFrame
    '''
    return read_dataset(path)

def convert_data_types(df):
    '''
    Make sure data types are correct
    '''
    df = df.rename(columns={'Catagory':'Category'})
    date_cols = [c for c in df.columns if 'date' in c.lower()]
    # df[date_cols] = pd.to_datetime(df[date_cols])
    for c in date_cols:
        df[c] = pd.to_datetime(df[c])
    df['Unit_Price'] = [float(re.sub(r'[\$,]', '',v)) for v in df['Unit_Price'].values]
    df['percentage'] = [float(re.sub(r'[\%,]', '',v)) / 100 for v in df['percentage'].values]
    return df
def add_fields(df):
    df['Revenue'] = (df['Sales_Volume'] * df['Unit_Price']).round(2)
    df['Inventory Value'] = df['Unit_Price'] * df['Stock_Quantity']
    df['Discontinued'] = df['Status'] == 'Discontinued'
    df['Low Stock'] = df['Stock_Quantity'] < df['Reorder_Level']
    df['Expired'] = df['Expiration_Date'] <= datetime.today()
    df['Restock'] = ((df['Low Stock'] == True) | (df['Expired'] == True)) & (df['Status'] == 'Active')
    return df
def load_df():
    '''
    Load DataFrame for analysis
    '''
    return add_fields(convert_data_types(dataset_to_frame(get_dataset())))

def rename_for_layout(df):
    mapping = {c : c.replace('_',' ').title() for c in df.columns}
    return df.rename(columns=mapping)
def rename_for_db(df):
    mapping = {c : c.replace(' ','_').title() for c in df.columns}
    return df.rename(columns=mapping)

def conda_env_to_requirements(path):
    '''
    Create a requirements.txt file for pip from conda env file
    '''
    with open(path,'r') as f:
        lines = f.readlines()[4:]
    new_lines = [l.rsplit('=',1)[0]+'\n' for l in lines]
    with open('requirements.txt','w') as f:
        f.writelines(new_lines)
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String,Float, DateTime, text,Boolean
import pandas as pd
import os
from .data import load_df

# Initialize SQLAlchemy engine

table = 'grocery'

def get_engine():
    '''
    Get sqlalchemy engine
    '''
    return create_engine('sqlite:///data.db', echo=True)

def db_exists():
    return os.path.exists('data.db')



def create_db(df,table=table,override=False):
    '''
    Create database with ecomm table
    '''
    if not db_exists() or override:
        # SQLAlchemy engine & metadata
        engine = get_engine()
        metadata = MetaData()
        df = df.rename(columns={c : c.replace(' ','_') for c in df.columns})
        dtypes = df.dtypes.astype(str).to_dict()
        column_mapping = {'int64':Integer,'float64':Float,'object':String,'datetime64[ns]':DateTime,'bool':Boolean}
        columns = (Column(k,column_mapping[v]) if k != 'Product_ID' else Column(k,column_mapping[v],primary_key=True) for k,v in dtypes.items())
        # Define symbols table (equivalent to a pandas DataFrame)
        _ = Table(table, metadata,
                  *columns
                              )
        # Create the table if it doesn't exist
        metadata.create_all(engine)

        # Insert DataFrame into SQLAlchemy table
        with engine.connect() as conn:
            df.to_sql(table, conn, if_exists='replace', index=False)

def list_tables():
    '''
    List table names
    '''
    engine = get_engine()
    with engine.connect() as connection:
        result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = result.fetchall()
        return [table[0] for table in tables]

def has_table(table):
    '''
    table exists
    '''
    return table in list_tables()

def get_all_data(order_by_col=None,ascending=False):
    engine = get_engine()
    # Fetch data using SQLAlchemy
    with engine.connect() as conn:
        query = f"SELECT * FROM {table} where Category is not null"
        if order_by_col:
            query += f'\norder by {order_by_col} {"desc" if not ascending else ""}'
        df = pd.read_sql(query, conn)
    return df



def initial_setup(override=False):
    if db_exists():
        if not has_table(table):
            df = load_df()
            # Call to create database and table on the first run
            create_db(df,override=override)
            return df
        return get_all_data()

    else:
        df = load_df()
        # Call to create database and table on the first run
        create_db(df,override=True)
        return df
        
 
def query_db(query):
    '''
    Read query
    '''
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(query, conn)
        

def insert_data(df,table):
    engine = get_engine()
    with engine.connect() as conn:
        df.to_sql(table, conn, if_exists='append', index=False)
def upsert_data(df,table):
    raise Exception("Not Implemented")
    engine = get_engine()
    with engine.connect() as conn:
        df['Date'] = df['Date'].dt.date
        conn.execute(
            text(f"""
            INSERT OR REPLACE INTO {table} 
            (Ticker, Date, Open, High, Low, Close, Volume)
            VALUES (:Ticker, :Date, :Open, :High, :Low, :Close, :Volume)
            """), df.to_dict(orient='records')
        )
def replace_data(df,table):
    engine = get_engine()
    df.to_sql(table, engine, if_exists='replace', index=False)


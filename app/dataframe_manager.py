import pandas as pd
from sqlalchemy import create_engine, text, inspect
import yfinance as yf
from datetime import datetime
class MySQLDataFrameManager:
    
    def __init__(self, host, user, password, database, port=3306):
        self.connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        print(f"Connecting to database at {host}:{port}/{database}")
        self.engine = create_engine(self.connection_string)

    
    def table_exists(self, table_name):
        """Check if table exists in database"""
        try:
            inspector = inspect(self.engine)
            exists = table_name in inspector.get_table_names()
            print(f"Checking table {table_name} exists: {exists}")  # Add logging
            return exists
        except Exception as e:
            print(f"Error checking table existence: {e}")  # Add logging
            return False
    def store_stock_data(self, ticker):
        """
        Fetch and store stock data from yfinance
        """
        try:
            # Check if table exists
            table_name = f"stock_{ticker.lower()}"
            print(f"Checking if table {table_name} exists...")
            
            # Fetch data from yfinance
            print(f"Fetching data for {ticker} from yfinance...")
            stock = yf.Ticker(ticker)
            df = stock.history(period="max")
            print(f"Retrieved {len(df)} rows of data")
            
            if df.empty:
                return False, f"No data available for ticker {ticker}"
            
            # Reset index to make date a column
            df.reset_index(inplace=True)
            
            # Ensure Date column is properly formatted
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"Columns in DataFrame: {df.columns.tolist()}")
            print(f"First row of data: {df.iloc[0].to_dict()}")
            
            # Store DataFrame
            print(f"Storing data in table {table_name}...")
            df.to_sql(
                name=table_name,
                con=self.engine,
                index=False,
                if_exists='replace'
            )
            print(f"Successfully stored data in table {table_name}")
            
            # Verify data was stored
            verify_query = f"SELECT COUNT(*) FROM {table_name}"
            count = pd.read_sql(verify_query, self.engine).iloc[0, 0]
            print(f"Verified {count} rows in database")
            
            return True, f"Successfully stored {count} rows of stock data for {ticker}"
            
        except Exception as e:
            print(f"Error in store_stock_data: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False, f"Error storing stock data: {str(e)}"

    def get_stock_data(self, ticker):
        """
        Retrieve stock data from database
        """
        try:
            table_name = f"stock_{ticker.lower()}"
            print(f"Attempting to retrieve data from table {table_name}")
            
            # Check if table exists
            inspector = inspect(self.engine)
            if table_name not in inspector.get_table_names():
                print(f"Table {table_name} not found in database")
                return None, f"No data found for ticker {ticker}"

            query = f"SELECT * FROM {table_name} ORDER BY Date DESC"
            print(f"Executing query: {query}")
            
            df = pd.read_sql(query, self.engine)
            print(f"Retrieved {len(df)} rows from database")
            
            return df, None
            
        except Exception as e:
            print(f"Error in get_stock_data: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None, f"Error retrieving stock data: {str(e)}"
    def store_dataframe(self, df, table_name, if_exists='replace'):
        """
        Store DataFrame to MySQL
        if_exists: 'fail', 'replace', or 'append'
        """
        try:
            df.to_sql(
                name=table_name,
                con=self.engine,
                index=False,
                if_exists=if_exists,
                chunksize=1000
            )
            return True, f"Successfully stored DataFrame to table '{table_name}'"
        except Exception as e:
            return False, f"Error storing DataFrame: {e}"

    def get_dataframe(self, table_name, columns=None, where_clause=None):
        """
        Retrieve DataFrame from MySQL
        """
        try:
            cols = "*" if columns is None else ", ".join(columns)
            query = f"SELECT {cols} FROM {table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"
            
            df = pd.read_sql(query, self.engine)
            return df, None
        except Exception as e:
            return None, f"Error retrieving DataFrame: {e}"

    def store_large_dataframe(self, df, table_name, chunk_size=10000):
        """
        Store large DataFrame in chunks
        """
        try:
            first_chunk = df.iloc[:chunk_size]
            first_chunk.to_sql(
                name=table_name,
                con=self.engine,
                index=False,
                if_exists='replace'
            )

            remaining_chunks = len(df) - chunk_size
            if remaining_chunks > 0:
                for start in range(chunk_size, len(df), chunk_size):
                    end = min(start + chunk_size, len(df))
                    chunk = df.iloc[start:end]
                    chunk.to_sql(
                        name=table_name,
                        con=self.engine,
                        index=False,
                        if_exists='append'
                    )

            return True, f"Successfully stored large DataFrame to table '{table_name}'"
        except Exception as e:
            return False, f"Error storing large DataFrame: {e}"

    def get_tables(self):
        """Get list of all tables"""
        try:
            query = "SHOW TABLES"
            df = pd.read_sql(query, self.engine)
            return df.values.flatten().tolist(), None
        except Exception as e:
            return None, f"Error getting tables: {e}"

    def get_table_info(self, table_name):
        """Get information about table columns"""
        try:
            query = f"DESCRIBE {table_name}"
            df = pd.read_sql(query, self.engine)
            return df, None
        except Exception as e:
            return None, f"Error getting table info: {e}"
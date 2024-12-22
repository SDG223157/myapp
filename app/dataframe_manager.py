import pandas as pd
from sqlalchemy import create_engine, text
import yfinance as yf
from datetime import datetime
class MySQLDataFrameManager:
    
    def __init__(self, host, user, password, database, port=3306):
        # Create SQLAlchemy engine
        self.engine = create_engine(
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        )

    
    def table_exists(self, table_name):
        """Check if table exists in database"""
        try:
            inspector = inspect(self.engine)
            return table_name in inspector.get_table_names()
        except Exception as e:
            print(f"Error checking table existence: {e}")
            return False

    def store_stock_data(self, ticker):
        """
        Fetch and store stock data from yfinance
        """
        try:
            # Check if table exists
            table_name = f"stock_{ticker.lower()}"
            if self.table_exists(table_name):
                return False, f"Stock data for {ticker} already exists"

            # Fetch data from yfinance
            print(f"Fetching data for {ticker}...")
            stock = yf.Ticker(ticker)
            df = stock.history(period="max")
            
            if df.empty:
                return False, f"No data available for ticker {ticker}"
            
            # Reset index to make date a column
            df.reset_index(inplace=True)
            
            # Convert all column names to strings
            df.columns = df.columns.astype(str)
            
            print(f"Storing data for {ticker}...")
            # Store DataFrame
            df.to_sql(
                name=table_name,
                con=self.engine,
                index=False,
                if_exists='replace'  # Changed from 'fail' to 'replace'
            )
            return True, f"Successfully stored stock data for {ticker}"
        except Exception as e:
            print(f"Error in store_stock_data: {e}")
            return False, f"Error storing stock data: {str(e)}"

    def get_stock_data(self, ticker):
        """
        Retrieve stock data from database
        """
        try:
            table_name = f"stock_{ticker.lower()}"
            if not self.table_exists(table_name):
                return None, f"No data found for ticker {ticker}"

            query = f"SELECT * FROM {table_name} ORDER BY Date DESC"
            df = pd.read_sql(query, self.engine)
            return df, None
        except Exception as e:
            print(f"Error in get_stock_data: {e}")
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
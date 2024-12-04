import pandas as pd
import numpy as np
from datetime import datetime
import re
import json
import logging
from typing import Dict, List, Any, Union
import sys

class SupabaseDataProcessor:
    """
    A class to process and validate CSV files for Supabase import.
    Handles data type validation, formatting, and common error cases.
    """
    
    VALID_TYPES = {
        'text': str,
        'varchar': str,
        'integer': int,
        'bigint': int,
        'decimal': float,
        'numeric': float,
        'boolean': bool,
        'date': 'date',
        'timestamp': 'timestamp',
        'json': 'json'
    }

    def __init__(self, input_file: str, schema_config: Dict[str, str], output_file: str):
        """
        Initialize the processor with input file, schema configuration, and output file.
        
        Args:
            input_file (str): Path to input CSV file
            schema_config (dict): Dictionary mapping column names to their Supabase types
            output_file (str): Path for processed output CSV file
        """
        self.input_file = input_file
        self.schema_config = schema_config
        self.output_file = output_file
        self.setup_logging()

    def setup_logging(self):
        """Configure logging for the processor"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('supabase_processing.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def validate_date(self, value: str) -> Union[str, None]:
        """Validate and format date strings"""
        try:
            if pd.isna(value):
                return None
            date_obj = pd.to_datetime(value)
            return date_obj.strftime('%Y-%m-%d')
        except:
            self.logger.warning(f"Invalid date format: {value}")
            return None

    def validate_timestamp(self, value: str) -> Union[str, None]:
        """Validate and format timestamp strings"""
        try:
            if pd.isna(value):
                return None
            timestamp_obj = pd.to_datetime(value)
            return timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
        except:
            self.logger.warning(f"Invalid timestamp format: {value}")
            return None

    def validate_json(self, value: str) -> Union[str, None]:
        """Validate and format JSON strings"""
        try:
            if pd.isna(value):
                return None
            if isinstance(value, str):
                # Ensure it's valid JSON
                json_obj = json.loads(value)
                return json.dumps(json_obj)
            return json.dumps(value)
        except:
            self.logger.warning(f"Invalid JSON format: {value}")
            return None

    def validate_number(self, value: Any, number_type: type) -> Union[int, float, None]:
        """Validate and format numeric values"""
        try:
            if pd.isna(value):
                return None
            return number_type(value)
        except:
            self.logger.warning(f"Invalid number format: {value}")
            return None

    def validate_boolean(self, value: Any) -> Union[bool, None]:
        """Validate and format boolean values"""
        if pd.isna(value):
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value = value.lower().strip()
            if value in ('true', 't', '1', 'yes', 'y'):
                return True
            if value in ('false', 'f', '0', 'no', 'n'):
                return False
        self.logger.warning(f"Invalid boolean format: {value}")
        return None

    def process_data(self) -> bool:
        """
        Process the input CSV file according to the schema configuration.
        
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            # Read the input CSV file
            self.logger.info(f"Reading input file: {self.input_file}")
            df = pd.read_csv(self.input_file)
            
            # Validate column names
            missing_columns = set(self.schema_config.keys()) - set(df.columns)
            if missing_columns:
                self.logger.error(f"Missing columns in input file: {missing_columns}")
                return False
            
            # Process each column according to its type
            for column, data_type in self.schema_config.items():
                self.logger.info(f"Processing column: {column} with type: {data_type}")
                
                if data_type not in self.VALID_TYPES:
                    self.logger.error(f"Invalid data type specified for column {column}: {data_type}")
                    return False
                
                # Apply appropriate validation based on data type
                if data_type == 'date':
                    df[column] = df[column].apply(self.validate_date)
                elif data_type == 'timestamp':
                    df[column] = df[column].apply(self.validate_timestamp)
                elif data_type == 'json':
                    df[column] = df[column].apply(self.validate_json)
                elif data_type in ('integer', 'bigint'):
                    df[column] = df[column].apply(lambda x: self.validate_number(x, int))
                elif data_type in ('decimal', 'numeric'):
                    df[column] = df[column].apply(lambda x: self.validate_number(x, float))
                elif data_type == 'boolean':
                    df[column] = df[column].apply(self.validate_boolean)
                
                # Handle null values
                df[column] = df[column].replace({np.nan: None})
            
            # Save processed data
            self.logger.info(f"Saving processed data to: {self.output_file}")
            df.to_csv(self.output_file, index=False, na_rep='NULL')
            self.logger.info("Processing completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing file: {str(e)}")
            return False

def main():
    # Example schema configuration
    schema_config = {
        'id': 'integer',
        'name': 'text',
        'email': 'varchar',
        'created_at': 'timestamp',
        'is_active': 'boolean',
        'metadata': 'json'
    }
    
    # Initialize and run the processor
    processor = SupabaseDataProcessor(
        input_file='input.csv',
        schema_config=schema_config,
        output_file='supabase_ready.csv'
    )
    
    success = processor.process_data()
    if success:
        print("CSV processing completed successfully!")
    else:
        print("CSV processing failed. Check the logs for details.")

if __name__ == "__main__":
    main()

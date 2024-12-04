# supabase-csv-format
A simple python script  for formatting a CSV file to work with Supabase.

## Don't forget to edit the scipt to work with your tables.

1. Create a schema configuration dictionary mapping your columns to Supabase types:
```
schema_config = {
    'column_name': 'data_type',
    # ... more columns
}
```
2. Initialize the processor with your files:
```
processor = SupabaseDataProcessor(
    input_file='your_input.csv',
    schema_config=schema_config,
    output_file='processed_output.csv'
)
```
3. Run the processing:
```
success = processor.process_data()
```

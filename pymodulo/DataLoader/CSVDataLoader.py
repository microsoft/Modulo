import pandas as pd
import warnings

from pymodulo.DataLoader.DataLoader import DataLoader

class CSVDataLoader(DataLoader):
    """Reads vehicle mobility data from a CSV.

    This is a child class of DataLoader that loads the vehicle mobility
    data from a CSV. Hence, it simply implements the `_prep_data` abstract
    class.

    """

    def __init__(self, csv_filepath, temporal_granularity, anonymize_data=False, mongo_uri='mongodb://localhost:27017/', db_name='modulo', collection_name='mobility_data'):
        # Call the constructor of the base class
        super().__init__(temporal_granularity, mongo_uri, db_name, collection_name)
        
        # Read CSV
        df = self._prep_data(csv_filepath)

        # Anonymize the data
        if anonymize_data:
            df, vehicle_id_mapping = self._anonymize_data(df)
            
            # Write the mappings dict as a JSON file
            with open('mappings.json', 'w') as f:
                json.dump(vehicle_id_mapping, f)

            warnings.warn(f"The mapping from original vehicle IDs to anonymized vehicle IDs has been stored in mappings.json. Please encrypt it!")

        # Insert the loaded data into the MongoDB database.
        self._insert_mobility_data(df)

    def _prep_data(self, csv_filepath):
        '''Loads a CSV into a Pandas dataframe.

        This is a private method.

        '''
        df = pd.read_csv(csv_filepath)

        # Ensure that the required columns exist in the df
        assert self._check_vehicle_mobility_df(df)

        return df

from abc import ABC, abstractmethod
import pymongo
from pymongo import MongoClient
import numpy as np
import pandas as pd
import random
import warnings

class DataLoader(ABC):

    """Handles loading of the vehicle mobility data and it's insertion into the database.

    This class handles the data heavy-loading for the user. It performs the
    following functions:
        - Load vehicle mobility data from the user's df
        - Anonymize it (if required)
        - Store it in a MongoDB dabatase
        - Create a geospatial index on the database
        - Compute the stratum ID and temporal ID for each datum.

    It also exposes public methods to fetch vehicle mobility data from the
    database. Users can use these methods to fetch their from the dabatase
    without requiring knowledge of MongoDB/pymongo.

    It accepts the following parameters:
        1) Temporal granularity (in seconds)
        2) MongoDB database information:
            - MongoDB URI: this is used to connect to the MongoDB server
            - Database name
            - Collection name (inside the database specified above)

    """

    def __init__(self, temporal_granularity, mongo_uri='mongodb://localhost:27017/', db_name='modulo', collection_name='mobility_data'):
        self.temporal_granularity = temporal_granularity
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name

    @abstractmethod
    def _prep_data(self):
        '''Reads data from a specific source.

        Each child class of this class implements this method. This method
        must contain the logic to read vehicle mobility data from that
        specific data source (e.g., CSV, JSON, GTFS, etc.) and return a
        Pandas df. This df must contain the following columns:
        vehicle_id (int), latitude (float), longitude (float),
        timestamp (int, in seconds).

        '''
        pass

    def _check_vehicle_mobility_df(self, df):
        """Checks existence of required columns names in the df.

        This is a protected method. The `_prep_data` method is defined in a
        child class of this class. Hence, it is important that we check the
        df that is returned from that method for correctness. Specifically,
        we need to check the existence of the following four columns:
        vehicle_id, latitude, longitude, timestamp. Also runs a few other
        checks like the types of these four columns.

        """

        required_columns = ['vehicle_id', 'latitude', 'longitude', 'timestamp']
        required_dtypes  = [np.dtype('int'), np.dtype('float'), np.dtype('float'), np.dtype('int')]


        for i in range(len(required_columns)):
            column = required_columns[i]
            dtype = required_dtypes[i]

            # check existence of this column
            if column not in df.columns:
                raise NameError(f"Column with name {column} not found in the dataframe.")

            # check data type of this column
            if df[column].dtype is not dtype:
                raise TypeError(f"Column {column} must be of type {dtype}.")

        return True

    def _anonymize_data(self, df):
        """Anonymizes the vehicle IDs in the vehicle mobility DataFrame.

        This is a protected method. Once the vehicle mobility data has been
        loaded into a DataFrame, the user may want to anonymize the vehicle
        IDs. This method does this anonymization.

        It replaces the vehicle IDs with the anonymized vehicle IDs and
        returns this anonymized df. It also returns the mapping between
        the original and anonymized vehicle IDs.

        """

        # Method:
        # Say we have n unique vehicle IDs. Then, generate a list of
        # integers: [0, ..., (n-1)]. Shuffle this list, and map the
        # integer at each index to the vehicle ID in the corresponding
        # index of the original list.
        vehicle_ids = df['vehicle_id'].unique().tolist()
        anonymized_vehicle_ids = list(range(len(vehicle_ids)))
        random.shuffle(anonymized_vehicle_ids)

        # Convert lists from above into a dict (mapping)
        vehicle_id_mapping = dict(zip(vehicle_ids, anonymized_vehicle_ids))

        # Replace original values in the vehicle_id column with
        # anonymized values
        df['vehicle_id'] = df['vehicle_id'].map(vehicle_id_mapping)

        return df, vehicle_id_mapping

    def _insert_mobility_data(self, df):
        """Reads vehicle mobility data from the df and inserts it into a MongoDB database.
        
        This is a protected method. This vehicle mobility data needs
        to be inserted into a MongoDB database for efficient geospatial
        querying of the data. This insertion is handled by this method.

        """

        client = MongoClient(self.mongo_uri)
        db = client[self.db_name]

        # first, before inserting, ensure that the given collection is empty
        num_docs = db[self.collection_name].count_documents({})

        if num_docs > 0:
            raise ValueError(f"The collection {self.collection_name} already contains {num_docs} documents. This function only creates a new collection afresh. Try specifying a different collection name or flushing the existing database/collection.")

        docs = []
        # read from df and prepare a list of docs to insert
        for idx, row in df.iterrows():
            lat = float(row['latitude'])
            lng = float(row['longitude'])
            vehicle_id = int(row['vehicle_id'])
            timestamp = int(row['timestamp'])  # in seconds

            docs.append({
                "vehicle_id": vehicle_id,
                "timestamp": timestamp,
                "location": {
                    "type": 'Point',
                    "coordinates": [lng, lat]
                }
            })

        # insert
        inserted_ids = []
        inserted_ids = db[self.collection_name].insert_many(docs).inserted_ids

        # prepare geospatial index on the collection
        _ = db[self.collection_name].create_index([('location', '2dsphere')])
        _ = db[self.collection_name].create_index([('timestamp', pymongo.ASCENDING)])

        client.close()

        if len(inserted_ids) == 0:
            warnings.warn("No data was inserted into the database. You might want to check if everything is as expected.")

        return len(inserted_ids)

    def compute_stratum_id_and_update_db(self, stratification_obj):
        """Computes the stratum ID for each datum in the database.

        Once the vehicle mobility data has been inserted into the database,
        we need to compute the stratum in which each GPS (mobility) datum
        falls into. Obviously, to find which stratum a GPS datum falls
        into, we need a list of all strata in the first place. Hence, we
        need the stratification object as an input to this method.
        
        Logic:
        Each stratum in the GeoJSON is a polygon. For each such stratum, we
        look for all GPS data points that lie inside of it, and write the
        stratum_id in the document representing the GPS data points (in the
        database).

        Returns the number of GPS points for which stratum_id was calculated
        and written into the database.

        """

        # Access the GeoJSON from the stratification object
        geojson_data = stratification_obj.input_geojson

        # create connection to the database using pymongo
        client = MongoClient(self.mongo_uri)
        db = client[self.db_name]

        # first, before updating, ensure that the given collection has been populated
        num_docs = db[self.collection_name].count_documents({})

        if num_docs == 0:
            raise ValueError(
                f"The collection {self.collection_name} has not already been populated by the vehicle mobility data. The data needs to be inserted into the database to be able to calculate stratum_id for each datum.")

        num_updated = 0

        for stratum in geojson_data['features']:
            stratum_id = stratum['properties']['stratum_id']
            geometry = stratum['geometry']

            # send mongo query to find all GPS points inside this stratum
            docs = db[self.collection_name].find({
                "location": {
                    "$geoWithin": {
                        "$geometry": geometry
                    }
                }
            })

            # for each found point, insert stratum_id
            for doc in docs:
                updated = db[self.collection_name].update_one({
                    "_id": doc['_id']
                }, {
                    "$set": {
                        "stratum_id": stratum_id
                    }
                }, upsert=False)

                num_updated += updated.modified_count

        # Sanity check
        if num_updated == 0:
            warnings.warn("No stratum ID was updated into the database. You might want to check if everything is as expected.")

        return num_updated

    def __get_time_segments(self, start_unixtime, end_unixtime):
        """Computes the list of time segments of a given duration from start time to end time.

        This is a private method. This method is a helper method which
        generates the list of time segments from thr beginning to the
        end.
            
        It takes a start timestamp (in seconds), end timestamp (in seconds)
        and temporal granularity (in seconds). It then generates buckets
        ("time segments") each of duration `self.temporal_granularity`,
        from start time to end time.

        Returns a list of 2-tuples. Each 2-tuple contains the start and end
        timestamps of the time segment.

        """

        interval_length = self.temporal_granularity

        time_boundaries = np.arange(start_unixtime, end_unixtime, interval_length).tolist() + [end_unixtime]
        time_segments = [(time_boundaries[i], time_boundaries[i + 1]) for i in range(len(time_boundaries) - 1)]

        return time_segments

    def compute_temporal_id_and_update_db(self):
        """Computes the temporal ID for each datum in the database.

        Computes the temporal_id (i.e., the "time bucket") that each datum
        in the vehicle mobility dataset falls into; and updates the datum's
        database record with this temporal_id.

        Returns the number of GPS points for which temporal_id was
        calculated and written into the database.

        """

        # Create connection to the database using pymongo
        client = MongoClient(self.mongo_uri)
        db = client[self.db_name]

        # First, before updating, ensure that the given collection has been populated
        num_docs = db[self.collection_name].count_documents({})

        if num_docs == 0:
            raise ValueError(f"The collection {self.collection_name} has not already been populated by the vehicle mobility data. The data needs to be inserted into the database to be able to calculate temporal_id for each datum.")

        min_time = db[self.collection_name].find_one({}, sort=[('timestamp', pymongo.ASCENDING)])['timestamp']
        max_time = db[self.collection_name].find_one({}, sort=[('timestamp', pymongo.DESCENDING)])['timestamp']

        # max_time + 1 --> because otherwise the time segmentation will always leave out
        # the latest GPS point because we use closed-left & open-right intervals. So,
        # the last timestamp gets left out due to the last segment's right-boundary being open.
        time_segments = self.__get_time_segments(min_time, max_time + 1)

        num_updated = 0

        # For each time segment, find the GPS points in that time segment
        for segment_start, segment_end in time_segments:
            docs = db[self.collection_name].find({
                'timestamp': {
                    '$gte': segment_start,
                    '$lt': segment_end
                }
            }, {
                '_id': 1
            })

            # For each such doc, run an update query to insert the temporal_id in the doc
            _ids = [doc['_id'] for doc in docs]

            updated = db[self.collection_name].update_many({
                "_id": {
                    "$in": _ids
                }
            }, {
                "$set": {
                    "temporal_id": segment_start  # temporal_id == start time of the segment it falls into
                }
            }, upsert=False)

            num_updated += updated.modified_count

        # Sanity check
        if num_updated == 0:
            warnings.warn("No temporal ID was updated into the database. You might want to check if everything is as expected.")

        return num_updated

    def fetch_data(self, query_filter=None, projection=None):
        """Returns a Pandas df containing the vehicle mobility data stored in the database.

        This is a helper function designed to fetch data stored in the
        database. Additionally, the user can specify any query filter or
        projection, if required.

        """

        # It is better to just not get the _id property as that is created
        # automatically by MongoDB. It's got nothing to do with our work.
        if projection is None:
            projection = {
                '_id': 0
            }

        # Create connection to the database using pymongo
        client = MongoClient(self.mongo_uri)
        db = client[self.db_name]

        # Query the database
        docs = db[self.collection_name].find(query_filter, projection)

        df = pd.DataFrame(docs)

        client.close()

        return df

    def fetch_data_for_vehicle_selection(self):
        """
        
        This is a helper function. It fetches the vehicle mobility data
        from the database and converts it to a format that is required by
        the vehicle selection algorithms.

        """

        query_filter = {
            'stratum_id': {
                '$exists': True
            },
            'temporal_id': {
                '$exists': True
            }
        }

        query_projection = {
            '_id': 0,
            'vehicle_id': 1,
            'stratum_id': 1,
            'temporal_id': 1
        }

        df = self.fetch_data(query_filter, query_projection)

        if len(df) == 0:
            raise ValueError(f"The resultant dataframe does not have any data.")

        # this operation finds the number of data points we have from a vehicle in a given stratum, per time segment
        df = df.groupby(['vehicle_id', 'stratum_id', 'temporal_id']).size().to_frame('count').reset_index()

        # <stratum ID>_<temporal ID> --> the spatiotemporal segment in which a datum lies
        df["spatiotemporal_segment"] = df['stratum_id'].astype(str) + "_" + df['temporal_id'].astype(str)

        return df


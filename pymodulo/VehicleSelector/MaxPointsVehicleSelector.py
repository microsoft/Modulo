from pymodulo.VehicleSelector.VehicleSelector import VehicleSelector

class MaxPointsVehicleSelector(VehicleSelector):
    """Select vehicles using MaxPoints algorithm.

    This algorithm selects vehicles using a simple heuristic: select the
    required number of vehicles as the topmost vehicles that have reported
    the highest number of datapoints in the vehicle mobility data.

    """

    def __init__(self, num_to_select, df, train_test_split_timestamp, coverage_metric='percentage_coverage'):
        super().__init__(num_to_select, df, train_test_split_timestamp, coverage_metric)

    def train(self):
        """Selects vehicles using this algorithm."""

        # keep the columns that we require
        df_train = self.df_train[['vehicle_id', 'count']]
        df_train = df_train.groupby(['vehicle_id']).sum()

        # Train, i.e. select vehicles
        df_train = df_train.sort_values(by=['count'], ascending=False)
        selected_vehicles = df_train.head(self.num_to_select).index.tolist()

        return selected_vehicles

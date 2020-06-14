import numpy as np

from pymodulo.VehicleSelector.VehicleSelector import VehicleSelector

class RandomVehicleSelector(VehicleSelector):
    """Select vehicles randomly.

    This algorithm simply selects the required number of vehicles randomly
    from the entire list of vehicles.

    """

    def __init__(self, num_to_select, df, train_test_split_timestamp, coverage_metric='percentage_coverage', random_seed=42):
        np.random.seed(random_seed)
        super().__init__(num_to_select, df, train_test_split_timestamp, coverage_metric)

    def train(self):
        """Selects vehicles using this algorithm."""
        
        vehicle_ids = self.df_train['vehicle_id'].unique().tolist()
        selected_vehicles = np.random.choice(vehicle_ids, self.num_to_select, replace=False).tolist()
        
        return selected_vehicles

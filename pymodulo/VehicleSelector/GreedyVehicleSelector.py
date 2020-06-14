import operator

from pymodulo.VehicleSelector.VehicleSelector import VehicleSelector

class GreedyVehicleSelector(VehicleSelector):
    """Select vehicles using a greedy approximation of the Maximum Coveraage Problem.

    This function selects vehicles by solving the best possible greedy
    approximation of the Maximum Coverage Problem. This formulation is
    explained further in our paper at ACM COMPASS 2020.

    """

    def __init__(self, num_to_select, df, train_test_split_timestamp, coverage_metric='percentage_coverage'):
        super().__init__(num_to_select, df, train_test_split_timestamp, coverage_metric)

    def __max_coverage_greedy_logic(self, df_train, vehicle_count):
        """Executes the greedy algorithm.
        
        This is a private method. It is a helper method that runs the
        main greedy logic.

        """
        
        total_vehicles = set(df_train['vehicle_id'].unique().tolist())
        total_vehicles_counts = len(total_vehicles)
        current_count = [];
        current_vehicles = [];
        iteration_count = []

        stats = dict(df_train['vehicle_id'].value_counts())
        first_vehicle = max(stats.items(), key=operator.itemgetter(1))[0]
        df_sel = df_train[df_train['vehicle_id'] == first_vehicle]

        current_vehicles.append(first_vehicle)
        current_coverage = df_sel['spatiotemporal_segment'].tolist()
        current_count.append(len(current_coverage))
        iteration_count.append(0)

        df_train = df_train[df_train['vehicle_id'] != first_vehicle];
        total_vehicles -= set([first_vehicle])

        for i in range(1, vehicle_count):
            if i <= total_vehicles_counts:
                candidate_vehicle = -1;
                candidate_coverage = list();
                candidate_count = current_count[-1]

                for vehicle in total_vehicles:
                    df_sel = df_train[df_train['vehicle_id'] == vehicle]
                    sel_vehicle_coverage = set(df_sel['spatiotemporal_segment'].tolist())

                    new_coverage = set(current_coverage).union(sel_vehicle_coverage)
                    new_count = len(new_coverage)
                    if new_count > candidate_count:
                        candidate_vehicle = vehicle
                        candidate_coverage = list(new_coverage)
                        candidate_count = new_count
                if candidate_vehicle > -1:
                    current_vehicles.append(candidate_vehicle)
                    current_count.append(candidate_count)
                    current_coverage = candidate_coverage
                    iteration_count.append(i)

                    df_train = df_train[df_train['vehicle_id'] != candidate_vehicle]
                    total_vehicles -= set([candidate_vehicle])
                else:
                    break

        return current_vehicles, current_coverage, current_count, iteration_count

    def train(self):
        """Selects vehicles using this algorithm."""

        df_train = self.df_train[['vehicle_id', 'spatiotemporal_segment', 'count']]
        
        # Train, i.e. select vehicles
        selected_vehicles, current_coverage, current_count, iteration_count = self.__max_coverage_greedy_logic(df_train, vehicle_count=self.num_to_select)
        
        return selected_vehicles

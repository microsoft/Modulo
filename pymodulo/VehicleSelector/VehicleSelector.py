from abc import ABC, abstractmethod
import pymodulo.metrics as metrics

class VehicleSelector(ABC):
    """Selects vehicles using a selection algorithm and reports coverage obtained by the selection.

    Once the vehicle mobility data has been uploaded to the database, this
    class finally runs vehicle Selection algorithms to select the desired
    number of vehicles from the entire set of vehicles. This vehicle
    selection process is called the "training" process. Once selected, the
    coverage obtained by this class is calculated using a coverage metric.
    This process is called the "test" process.

    It takes the following inputs:
        1) Number of vehicles to select
        2) DataFrame containing vehicle mobility data.
        3) UNIX Timestamp (in seconds) at which to divide into train-test
        4) Coverage metric to use for the testing process

    """

    def __init__(self, num_to_select, df, train_test_split_timestamp, coverage_metric='percentage_coverage'):

        # Small check:
        #   Can't select more vehicles than are available!
        if num_to_select > len(df['vehicle_id'].unique()):
            raise ValueError("Can't select more vehicles than are available.")

        self.num_to_select = num_to_select
        self.train_test_split_timestamp = train_test_split_timestamp
        self.df = df
        self.__train_test_splitter()
        self.coverage_metric_function = self.__decide_metric_function(coverage_metric)


    def __train_test_splitter(self):
        """Splits vehicle mobility data into train and test.

        This is a private method. It is a helper method to do the
        splitting into train and test.

        """

        self.df_train = self.df[self.df['temporal_id'] <= self.train_test_split_timestamp]
        self.df_test = self.df[self.df['temporal_id'] > self.train_test_split_timestamp]

    def __decide_metric_function(self, coverage_metric):
        """Decides which coverage metric function to use for testing.
        
        This is a private method. It is a helper method.
        The coverage metric inputted by the user (as a parameter) is either
        a string or a function. If it is a string, this method ensures that
        this metric is supported. If it is a function, returns that function
        itself as the coverage metric function.

        """

        if type(coverage_metric) is str:
            try:
                coverage_metric_function = metrics.METRICS_LIST[coverage_metric]
            except KeyError as e:
                raise ValueError(
                    f"Coverage metric {coverage_metric} is not supported. You can define your own function and pass that as an argument instead.")
        else:
            coverage_metric_function = coverage_metric

        return coverage_metric_function

    def __test_vehicle_selection(self, selected_vehicles, df_test, coverage_metric_function):
        """Computes the coverage obtained by selected vehicles.
        
        This is a private method. It is a helper method.
        Once the vehicle selection (i.e., the training) is done, we need to
        report what coverage is obtained by this selection. This coverage
        is obtained using a metric: `coverage_metric_function`. This
        coverage is obtained on the basis of these vehicles' mobility data
        as given by `df_test`.

        Returns a dict containing selected vehicles and the coverage obtained.

        """

        coverage = coverage_metric_function(selected_vehicles, df_test)

        test_results = {
            'selected_vehicles': selected_vehicles,
            'coverage': coverage
        }

        return test_results

    def test(self, selected_vehicles):
        """Computes the coverage obained by the vehicles selected."""

        test_results = self.__test_vehicle_selection(selected_vehicles, self.df_test, self.coverage_metric_function)
        
        return test_results

    @abstractmethod
    def train(self):
        """Executes the logic used to select the vehicles.

        Each child class of this class implements its own logic or
        heuristic to select vehicles from the larger set.

        """

        pass

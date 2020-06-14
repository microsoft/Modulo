"""
    This module contains implementation(s) of the coverage metric(s).

    Functions in this module will be called to compute the coverage
    resulting from a set of vehicles selected using any of the vehicle
    selection algorithms. Obviously, these metric functions also require
    the mobility data of the selected vehicles to compute their coverage.

"""

def percentage_coverage(selected_vehicles_list, df):
    '''
        `selected_vehicles_list` is the list of (selected) vehicles that we
        want to (virtually) deploy.
        `df` is a Pandas dataframe that contains the vehicle mobility data
        on the basis of which the coverage will be caluclated.
        
        In other words, what coverage would we get if we had deployed
        sensors on `selected_vehicles_list` and they had travelled
        according to the mobility data in `df`?

        Formula: (Spatiotemporal segments covered by selected vehicles) / (spatiotemporal segments covered by ALL vehicles)
    '''

    # First, calculate the list of unique spatiotemporal segments covered by ALL vehicles (the denominator)
    all_vehicles_coverage_set = df['spatiotemporal_segment'].unique().tolist()

    # Then, compute the list of unique spatiotemporal segments covered by the selected vehicles (the numerator)
    selected_vehicles_coverage_set = df[ df['vehicle_id'].isin(selected_vehicles_list) ]['spatiotemporal_segment'].unique().tolist()
    
    coverage = len(selected_vehicles_coverage_set)/len(all_vehicles_coverage_set) * 100

    return coverage

# List of all metrics with their string identifiers as the keys
METRICS_LIST = {
    'percentage_coverage': percentage_coverage
}
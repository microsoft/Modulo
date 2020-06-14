from abc import ABC, abstractmethod

class SpatialStratification(ABC):
    """Handles stratification of the geographic area-of-interest.

    This class "stratifies" the area-of-interest. It's child classes offer
    different methods of stratification: square grids (GridStratification),
    only roads (RoadStratification), or any custom stratification
    (CustomStratification).

    This list of offered stratification types may grow with time.
    
    """

    def __init__(self):
        self.input_geojson = None

    @abstractmethod
    def _check_inputs(self):
        """Checks correctness of parameters for each stratification type.

        For each child child class, this method is required to check the
        parameters that define that particular stratification type. The
        stratification proceeds if these checks pass.
            
        """

        pass

    @abstractmethod
    def stratify(self):
        """Executes the logic for each stratification type.

        This method defines the logic that divides the area-of-interest
        into a strata. Finally, it creates a GeoJSON object containing the
        strata as polygons. It also assigns a stratum ID to each generated
        stratum.

        """

        pass

    def _assign_stratum_id(self, input_geojson):
        """Assigns stratum ID to each stratum.

        Protected method. This method accepts a GeoJSON representing the
        stratification of the area-of-interest. It inserts a stratum ID for
        each stratum in the GeoJSON object. Finally, it returns the same
        GeoJSON, but with added stratum IDs.

        """

        if not isinstance(input_geojson, dict):
            raise TypeError("input_geojson must be a valid GeoJSON dict.")

        # Go through each feature in the GeoJSON object
        for i in range(len(input_geojson['features'])):
            # Insert the stratum_id in the feature's `properties` property.
            # This is just GeoJSON convention.
            if 'properties' not in input_geojson['features'][i]:
                input_geojson['features'][i]['properties'] = {}
            input_geojson['features'][i]['properties']['stratum_id'] = i

        return input_geojson
import logging

from pymodulo.SpatialStratification.SpatialStratification import SpatialStratification

class CustomStratification(SpatialStratification):
    """Stratifies the area-of-interest into any custom polygons.

    This is a child class of SpatialStratification that implements any
    custom stratification. Hence, it accepts the GeoJSON as an input from
    the user itself.

    """

    def __init__(self, input_geojson):
        super().__init__()

        is_correct, msg = self._check_inputs(input_geojson)

        if is_correct:
            self.input_geojson = input_geojson
        else:
            logging.error(msg)
            raise ValueError(msg)

    def _check_inputs(self, input_geojson):
        """Checks custom stratification GeoJSON input by the user.

        This is a private method.

        """
        
        # Ensure that each feture is of type "Polygon".
        for feature in input_geojson['features']:

            if feature['geometry']['type'] != 'Polygon':
                return False, "Custom GeoJSON must contain only Polygon types. No other GeoJSON type is supported."

        return True, ""

    def stratify(self):
        """Executes the logic to finally do the stratification.

        Since the GeoJSON is already given by the user in this case, we
        only need to assign a stratum ID to each stratum in the
        user-provided GeoJSON.

        """

        # Assign stratum IDs to each stratum in the GeoJSON
        self.input_geojson = self._assign_stratum_id(self.input_geojson)
        logging.info("GeoJSON created!")

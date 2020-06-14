import logging
import subprocess
import json
import os

from pymodulo.SpatialStratification.SpatialStratification import SpatialStratification

class GridStratification(SpatialStratification):
    """Stratifies the area-of-interest into square grids/cells.

    This is a child class of SpatialStratification that implements a square
    grid stratification. It accepts the area-of-interest as a bounding-box.
    It invokes a JavaScript library, Turf.js, to do this gridification.
    It also assigns a stratum_id to each generated stratum (in this case,
    to each grid/cell).

    It accepts:
        1) the side length of each cell in the grid (in kilometers).
        2) the bounding-box as separate arguments:
           min_longitude, min_latitude, max_longitude, max_latitude

    """

    def __init__(self, cellSideLength, min_longitude, min_latitude, max_longitude, max_latitude):
        super().__init__()

        is_correct, msg = self._check_inputs(cellSideLength, min_longitude, min_latitude, max_longitude, max_latitude)
        
        if is_correct:
            self.cell_side = cellSideLength
            self.min_lng = min_longitude
            self.min_lat = min_latitude
            self.max_lng = max_longitude
            self.max_lat = max_latitude
        else:
            logging.error(msg)
            raise ValueError(msg)

    def _check_inputs(self, cellSideLength, min_longitude, min_latitude, max_longitude, max_latitude):
        """Checks grid stratification parameters input by the user.

        This is a private method.

        """

        if cellSideLength <= 0:
            return False, "Cell side length has to be greater than 0."
        if min_latitude >= max_latitude:
            return False, "Minimum latitude has to be smaller than maximum latitude"
        if min_longitude >= max_longitude:
            return False, "Minimum longitude has to be smaller than maximum longitude"
        if not (-90 <= min_latitude <= 90):
            return False, "Minimum latitude has to be within the range [-90, 90]"
        if not (-90 <= max_latitude <= 90):
            return False, "Maximum latitude has to be within the range [-90, 90]"
        if not (-180 <= min_longitude <= 180):
            return False, "Minimum longitude has to be within the range [-180, 180]"
        if not (-180 <= max_longitude <= 180):
            return False, "Maximum longitude has to be within the range [-180, 180]"

        return True, ""

    def stratify(self):
        """Executes the logic to finally do the stratification.

        The bounding-box and the cell-side length are handed over to a
        Node.js library, Turf.js. This part of our library causes a
        dependency on Node.

        """

        # This is required because current working directory will the place where
        # the user ran their script from, not THIS directory.
        this_file_directory = os.path.dirname(os.path.abspath(__file__))

        # Delegate this task to the Turf.js package using Node.js
        process = subprocess.Popen([f"node {this_file_directory}/gridding.js {self.min_lng} {self.min_lat} {self.max_lng} {self.max_lat} {self.cell_side}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = process.communicate()

        if err:
            raise RuntimeError(f"There was an error in running node.js: {err.decode('utf-8')}")
        
        # If there was no error, we decode the output from the node
        # script into a JSON (actually, GeoJSON) format.
        out = out.decode('utf-8')
        input_geojson = json.loads(out)

        # Assign stratum IDs to each stratum in the GeoJSON created by Turf.js
        self.input_geojson = self._assign_stratum_id(input_geojson)
        logging.info("GeoJSON created!")

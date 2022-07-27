// npm install @turf/turf

const turf = require('@turf/turf');

// User specified parameters.

// Read bbox values from the command-line.
let bbox = [process.argv[2], process.argv[3], process.argv[4], process.argv[5]]
bbox = bbox.map((val, i) => {
	return parseFloat(val);
});
// bbox is now something like: [77.52021789550781, 12.91823730850926, 77.68020629882812, 13.02997975435598]

let cellSide = Number(process.argv[6]);
let options = {units: 'kilometers'};

// use turfjs to get the grid
let squareGrid = turf.squareGrid(bbox, cellSide, options);

// add stratum_id to each cell
squareGrid.features = squareGrid.features.map((grid, i) => {
	grid['properties']['stratum_id'] = i;
	return grid;
});

console.log(JSON.stringify(squareGrid));
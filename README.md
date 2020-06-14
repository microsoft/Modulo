# modulo

*Drive-by* sensing is a popular upcoming approach for monitoring large geographic areas using a fleet of vehicles equipped to sense relevant quantities. Prior research has shown the efficacy of drive-by sensing in monitoring air pollution, detecting potholes, recognizing unsafe pedestrian movement, etc.

Assume a scenario in which a sensor network administrator decides to install 10 sensors on vehicles to sense a quantity.  The administrator may have a much larger fleet of vehicles, say 100 vehicles, to choose these 10 vehicles from. How does the administrator decide which 10 of the 100 available vehicles to choose, such that his/her choice maximizes the spatiotemporal coverage? We introduce Modulo --- a system for vehicle selection in drive-by sensing.

## Installation and Pre-requisites

Modulo is primarily written in Python and supports Python version `>=3.6`. You can install Modulo using:

```bash
pip3 install pymodulo
```

Modulo also has a few other non-Python dependencies:
 1. MongoDB
     Please ensure you have access to a MongoDB server (local or remote). If you prefer a quick and simple remote MongoDB server, you can try out [MongoDB Atlas](https://www.mongodb.com/cloud/atlas). Instead, if you prefer installing a local server, you can do so from [here](https://www.mongodb.com/try/download/community). If you choose to install it locally, we also suggest installing a MongoDB GUI like [MongoDB Compass](https://www.mongodb.com/products/compass).
2. Node.js and NPM
    Modulo uses [Turf.js](https://turfjs.org/), a JavaScript library available on NPM. You can download the `package.json` available in this repository, place it in the root of your project, and simply do:
    ```bash
    npm init
    npm install
    ```
    Please ensure that the Node.js is accessible as the `node` command on the terminal.

## How to Run

Please follow the iPython notebook available in this repository (`example.ipynb`).

The code is well-documented using Python docstrings. Hence, you can use Python's `help()` feature on any class or method to know more about what it does.

## Citing this work

If you find Modulo useful for your research work, please cite us as follows:

Dhruv Agarwal, Srinivasan Iyengar, et al. Modulo: Drive-by sensing at city-scale on the cheap. InProceedings of the 3rd ACM SIGCAS Conference on Computing and Sustainable Societies 2020.

```bash
@inproceedings{agarwal2020modulo,
  title={Modulo: Drive-by sensing at city-scale on the cheap},
  author={Agarwal, Dhruv and Iyengar, Srinivasan and Swaminathan, Manohar and Sharma, Eash and Raj, Ashish and Hatwar, Aadithya},
  booktitle={Proceedings of the 3rd ACM SIGCAS Conference on Computing and Sustainable Societies},
  year={2020}
}
```
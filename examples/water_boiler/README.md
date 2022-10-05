# Water Boiler Example

Simple simulation of a water boiler which can heat up water and where the heat dissipates slowly over time. Running the example will run the water boiler simulation for 10 seconds and use the PID controller to make the boiler reach a setpoint temperature. The results will also be plotted using [Matplotlib](https://matplotlib.org).

## Installation

It's recommended to install the dependencies (numpy and matplotlib, in addition to the simple-pid library itself) in a virtual environment.

```bash
# Linux:
python -m venv venv
. venv/bin/activate

# Windows:
python -m venv venv
venv/Scripts/activate
```

Then install the example dependencies:

```bash
python -m pip install ../..[examples]
```

## Usage

```bash
# Activate the virtual environment if you use one:
. venv/bin/activate

# Run the example:
python water_boiler.py

# Once you're done deactivate the virtual environment if you use one:
deactivate
```

## Troubleshooting

### Ubuntu

Depending on your environment, you might have to [install a some system dependencies for Matplotlib](https://stackoverflow.com/a/56673945/3767264) to display the graph.

Typically, the sign of that is usually one the following errors:

- `UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.`
- `AttributeError: module 'cairo' has no attribute 'version_info'` (if the system dependencies are already available but not the corresponding Python dependencies)

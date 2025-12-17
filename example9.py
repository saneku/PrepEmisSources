from src import *
import argparse

# Example read:
# Demonstrates how to reconstruct and plot an emission scenario directly from an
# existing wrfchem emission NetCDF file that was produced by PrepEmisSources.

#python example_read.py wrfchemv_d01.2025-11-23_08\:30\:00 --material ash
#python example_read.py wrfchemv_d01.2025-11-23_08\:30\:00 --material so2

def parse_args():
    parser = argparse.ArgumentParser(
        description="Load an emission scenario from a wrfchem NetCDF file and plot it."
    )
    parser.add_argument(
        "--nc-file",
        default="wrfchemv_d01.2025-11-23_08:30:00",
        help="Path to the wrfchem emission NetCDF file.",
    )
    parser.add_argument(
        "nc_file_pos",
        nargs="?",
        help="Optional positional path to the wrfchem emission NetCDF file.",
    )
    parser.add_argument(
        "--material",
        default="so2",
        choices=["ash", "so2", "sulfate", "watervapor"],
        help="Which emission species to read.",
    )
    parser.add_argument(
        "--lat",
        type=float,
        default=13.51,
        help="Volcano latitude used when locating the cell (ignored if x/y supplied).",
    )
    parser.add_argument(
        "--lon",
        type=float,
        default=40.722,
        help="Volcano longitude used when locating the cell (ignored if x/y supplied).",
    )
    parser.add_argument(
        "--x",
        type=int,
        default=None,
        help="Optional west_east index of the emission cell (overrides lat/lon).",
    )
    parser.add_argument(
        "--y",
        type=int,
        default=None,
        help="Optional south_north index of the emission cell (overrides lat/lon).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    nc_path = args.nc_file_pos or args.nc_file

    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    scenario = netcdf_handler.load_scenario_from_file(
        material=args.material,
        nc_path=nc_path,
        lat=args.lat,
        lon=args.lon,
        x=args.x,
        y=args.y,
    )

    print(scenario)
    print(f"Profiles: {scenario.getNumberOfProfiles()}, total mass: {scenario.getScenarioEmittedMass():.3f} Mt")
    
    scenario.plot()
    
    print ("\n\n\nThe scenario can be used to recreate the scenario object using EmissionWriter_NonUniformInHeightProfiles, as in example6.py:\n")
    print(repr(scenario))

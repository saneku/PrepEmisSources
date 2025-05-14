The modular architecture

the object-oriented design, emphasizing modularity for different eruption types. 
Object-oriented Python architecture
This modular design allows for great flexibility in creating realistic emission scenarios for atmospheric modeling.


The code is related to modeling emissions from volcanic eruptions or similar events.

The system models how emissions are distributed over time and altitude

The interpolation methods allow adjusting temporal and vertical

There is the Emission class, which is abstract, and VerticalProfile handling altitude distributions. The EmissionScenario class manages multiple profiles, normalizes mass, and handles time and height interpolation.



the ability to handle different temporal resolutions helps in aligning with model input requirements. 

Mass fraction values at different altitudes





- `EmissionScenario` class orchestrates complete emission events:
  - Manages collections of VerticalProfile instances
  - Handles temporal interpolation (60-minute resolution default)
  - Performs vertical height adjustment using linear interpolation
  - Implements mass conservation through normalization
  - Maintains emission metadata (start/end datetime, total mass)







# PrepEmis: A Framework for Atmospheric Emission Scenario Modeling

## Overview

PrepEmis is a computational framework designed for the preparation, manipulation, and visualization of atmospheric emission scenarios. 
The system provides a flexible infrastructure for handling vertical emission profiles with temporal and spatial dimensions, particularly suited for modeling volcanic eruptions and other atmospheric emission events.

## Core Functionality

The framework centers around the `EmissionScenario` class, which manages collections of vertical emission profiles. Each profile represents the vertical distribution of emitted material at a specific time point. 

The system implements an object-oriented architecture with inheritance to support different types of emission scenarios. 
The `EmissionScenario_InvertedPinatubo` class demonstrates the framework's ability to handle specific historical eruption data, while maintaining the flexibility to accommodate various emission types through the abstract `Emission` class.

The vertical profiles are managed through the `VerticalProfile` class, which maintains both the height distribution and temporal information for each emission time step, enabling sophisticated four-dimensional (space and time) emission modeling.







# PrepEmis Framework Class Descriptions

## Core Classes

### `WRFNetCDFWriter`
A class responsible for handling NetCDF file operations for WRF (Weather Research and Forecasting) model input/output. 
A class for writing emission data to NetCDF files compatible with WRF (Weather Research and Forecasting) model.

It provides methods to:
- Read data from WRF input files
- Prepare emission files with appropriate dimensions and variables
- Find the closest grid cell to a given latitude/longitude
- Extract vertical column information (heights and layer thicknesses)
- Write emission data to NetCDF files
- Visualize the total emitted mass over time

### `EmissionScenario`
Base class for managing emission scenarios. It maintains a collection of vertical profiles and provides methods to:
- Add vertical profiles to the scenario
- Normalize profiles by total mass
- Interpolate profiles in time and height
- Adjust profiles for grid cell thickness
- Plot the scenario for visualization
- Retrieve start and end times of the emission event

### `EmissionScenario_MixOfProfiles`
A specialized implementation of `EmissionScenario` that allows combining different types of vertical profiles for a single emission type.


### `EmissionScenario_InvertedPinatubo`
A specialized emission scenario class for handling inverted emission profiles from the Pinatubo eruption.
- **Parameters**:
  - `type_of_emission`: An emission object (Ash, SO2, WaterVapor)
  - `filename`: Path to the file containing the inverted emission profiles
- **Functionality**:
  - Loads pre-computed emission profiles from pickle files
  - Creates vertical profiles based on the loaded data
  - Maintains the staggered height grid from the original data
  - Handles temporal evolution of the emission


### `EmissionWriter`
Base class for writing emission scenarios to NetCDF files.

### `EmissionWriter_UniformInTimeProfiles`
A specialized implementation of `EmissionWriter` that handles emission scenarios with uniform time intervals between profiles.



### `EmissionWriter_NonUniformInTimeProfiles`
A specialized writer class for handling emission scenarios with non-uniform time intervals.
- **Parameters**:
  - `scenarios`: List of emission scenarios to write
  - `netcdf_handler`: A WRFNetCDFWriter instance
  - `output_interval`: Time interval in minutes for output (10 in this example)
- **Functionality**:
  - Interpolates emission profiles to the specified time interval
  - Converts emission units from Mt to Mt/m by dividing by grid cell height
  - Normalizes profiles by total mass
  - Writes emission data to NetCDF files through the netcdf_handler



## Emission Classes

### `Emission`
Base class for all emission types, containing common properties like mass, latitude, and longitude.

### `Emission_Ash`
Class representing volcanic ash emissions. Features include:
- Support for different ash bin configurations (4 or 10 bins)
- Computation of ash mass fractions based on lognormal distribution parameters
- Custom setting of mass fractions across bins
- Default parameters for mean radius and standard deviation
  - Computes ash mass fractions across bins based on lognormal distribution
  - Distributes total ash mass across different particle size bins
  - Provides methods to customize mass distribution

### `Emission_SO2`
Class representing sulfur dioxide emissions.

### `Emission_Sulfate`
Class representing sulfate aerosol emissions.

### `Emission_WaterVapor`
Class representing water vapor emissions.

## Vertical Profile Classes

### `VerticalProfile`
Base class for all vertical profiles, containing the vertical distribution of emissions and methods to:
- Normalize profiles
- Interpolate to different vertical grids
- Plot the profile

### `VerticalProfile_Zero`
A profile with zero emissions at all levels, typically used to represent periods of inactivity.

### `VerticalProfile_Uniform`
A profile with uniform emission distribution between specified minimum and maximum heights.

### `VerticalProfile_Umbrella`
A profile representing the classic umbrella-shaped distribution of volcanic eruptions, with parameters to control:
- Maximum emission height
- Vent height
- Percentage of mass in the umbrella region
- Distribution of remaining mass in the eruption column

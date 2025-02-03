from emissions.types import AshEmission, SO2Emission, SulfateEmission, WaterVaporEmission
from profiles.types import UniformProfile, SuzukiProfile, InvertedProfile
from core.eruption import Eruption
from core.netcdf_handler import NetCDFHandler
from core.writer import EmissionWriter

if __name__ == "__main__":
    emissions = [
        AshEmission(mean=50, stddev=10, location="A", amount=100, duration=5, start_time="12:00"),
        SO2Emission(mean=10, stddev=0.5, location="B", amount=200, duration=10, start_time="14:00"),
        SulfateEmission(mean=2, stddev=1, location="C", amount=150, duration=7, start_time="16:00"),
        WaterVaporEmission(mean=30, stddev=5, location="D", amount=50, duration=3, start_time="18:00")
    ]


    erup_duration=[600]    #minutes

    volc_ash_emis_0=[60.0] #Mt
    volc_so2_emis_0=[15.0] #Mt
    volc_sulf_emis_0=[0.0] #Mt
    volc_qv_emis_0=[150.0] #Mt




    netcdf_handler = NetCDFHandler(source_file="source.nc", destination_file="output.nc")
    emission_writer = EmissionWriter(emissions, netcdf_handler)

    eruption = Eruption()
    for emission in emissions:
        eruption.add_emission(emission)

    eruption.add_profile(UniformProfile())
    eruption.add_profile(SuzukiProfile())
    eruption.add_profile(InvertedProfile())

    emission_writer.write_emissions_to_netcdf()

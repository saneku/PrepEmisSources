#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
#                                                                            #
#    This file is part of PVAI - Python Volcanic Ash Inversion.              #
#                                                                            #
#    Copyright 2019, 2020 The Norwegian Meteorological Institute             #
#               Authors: André R. Brodtkorb <andreb@met.no>                  #
#                                                                            #
#    PVAI is free software: you can redistribute it and/or modify            #
#    it under the terms of the GNU General Public License as published by    #
#    the Free Software Foundation, either version 2 of the License, or       #
#    (at your option) any later version.                                     #
#                                                                            #
#    PVAI is distributed in the hope that it will be useful,                 #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#    GNU General Public License for more details.                            #
#                                                                            #
#    You should have received a copy of the GNU General Public License       #
#    along with PVAI. If not, see <https://www.gnu.org/licenses/>.           #
#                                                                            #
##############################################################################

import os
import numpy as np
import datetime
import json


def aPosterioriToSourceTerm(filename, outfilename, variable):
    #Read data
    with open(filename, 'r') as infile:
        json_string = infile.read()

    #Parse data
    json_data = json.loads(json_string)

    #Copy only data we care about
    emission_times = np.array(json_data["emission_times"], dtype='datetime64[ns]')
    level_heights = np.array(json_data["level_heights"], dtype=np.float64)
    level_altitudes = np.cumsum(np.concatenate(([0], level_heights)))

    ordering_index = np.array(json_data["ordering_index"], dtype=np.int64)
    data = np.array(json_data[variable], dtype=np.float64)

    residual = np.array(json_data["residual"], dtype=np.float64)
    convergence = np.array(json_data["convergence"], dtype=np.float64)

    arguments = json_data["arguments"]
    config = json_data["config"]
    run_date = np.array(json_data["run_date"], dtype='datetime64[ns]')

    def npTimeToDatetime(np_time):
        return datetime.datetime.utcfromtimestamp((np_time - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's'))

    def npTimeToStr(np_time, fmt="%Y-%m-%d %H:%M:%S"):
        return npTimeToDatetime(np_time).strftime(fmt)

    header = """\
# This file describes the emission heighs and strengths.
#
# NAME, TRACER, LEVEL_TYPE, LEVEL, EMISSION_RATE_TYPE, EMISSION_RATE, , EMISSION_START, EMISSION_END, COMMENT
# NAME: Points to columnsource_location.csv, last column
# TRACER: tracer group (hard coded in source code),
#         ASH_L01 - ASH_L19
# LEVEL_TYPE: Vertical level id to emit into
#         SLEV corresponds to the levels in Vertical_levels.txt. However
#         these levels are MLEV => model levels, and have 0 at the top, whilst
#         SLEV has 0 at ground.
# LEVEL: Level index to emit into
#         1..nlevels
# EMISSION_RATE_TYPE: Type of emission rate
#         EVENT: Emit X Tg for whole duration of event
# EMISSION_RATE: Rate of emission in Tg if EVENT above
# EMISSION_START: Start of emission
#         SR - start of run.
# EMISSION_END: End of emission
#         SR+H1 - start of run + 1 hour
# COMMENT - description
"""


    with open(outfilename, 'wt') as outfile:
        outfile.write(header)

        for t in range(len(emission_times)):
            for a in range(len(level_heights)):
                emis_index = ordering_index[a, t]
                if (emis_index >= 0):
                    level = a+1
                    start = npTimeToStr(emission_times[t])
                    end = npTimeToStr(emission_times[t] + np.timedelta64(3, 'h'))
                    altitude = (level_altitudes[a] + level_altitudes[a+1]) // 2
                    source_term = data[emis_index]

                    source_term_str = "ASHinv,ASH_L01,SLEV,{:02d},EVENT,{:f},,{:s},{:s},alt={:.0f}\n".format(level, source_term, start, end, altitude)
                    if (source_term < 0):
                        outfile.write("# " + source_term_str)
                    else:
                        outfile.write(source_term_str)



if __name__ == "__main__":
    import configargparse

    parser = configargparse.ArgParser(description='A posteriori information to EMEP source term.')
    parser.add("-j", "--json", type=str, help="JSON-file to convert", default=None, required=True)
    parser.add("-v", "--variable", type=str, help="Output file", default='a_posteriori_2d')
    parser.add("-o", "--output", type=str, help="Output file", default=None)
    args = parser.parse_args()

    print("Arguments: ")
    print("=======================================")
    for var, val in vars(args).items():
        print("{:s} = {:s}".format(var, str(val)))
    print("=======================================")

    outfile = args.output
    if outfile is None:
        basename, ext = os.path.splitext(os.path.abspath(args.json))
        outfile = basename + "_emep_source.csv"

    if (args.json is not None):
        print("Writing output to " + outfile)
        aPosterioriToSourceTerm(args.json, outfile, variable=args.variable)

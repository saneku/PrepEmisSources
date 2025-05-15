#!/usr/bin/env python
# -*- coding: utf-8 -*-

 #python Plot.py -j ./inversion_000_1.00000000_a_posteriori_reference.json --unit='kg/(m*s)' --output='out.png'

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

if __name__ == "__main__":
    import matplotlib as mpl
    mpl.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap, LogNorm, TwoSlopeNorm, SymLogNorm
import numpy as np
import datetime
import json
import os


def makePlotFromJson(json_filename, outfile=None, **kwargs):
    json_data = readJson(json_filename, **kwargs)
    fig, axs = plotAshInv(json_data, **kwargs)

    if (outfile is not None):
        basename, ext = os.path.splitext(os.path.abspath(outfile))
        if (ext == 'pdf'):
            saveFig(outfile, fig, json_data["meta"])
        else:
            fig.savefig(outfile)

    return fig, axs


def readJson(json_filename, 
        prune=True, 
        prune_zero=0, 
        valid_times_min=None, 
        valid_times_max=None,
        **kwargs):
    #Read data
    with open(json_filename, 'r') as infile:
        json_string = infile.read()

    #Parse data
    json_data = json.loads(json_string)

    #Add metadata to json_data
    json_data["filename"] = os.path.abspath(json_filename)
    json_data["meta"] = json.dumps(json_data)

    #Parse data we care about
    json_data["emission_times"] = np.array(json_data["emission_times"], dtype='datetime64[ns]')
    json_data["level_heights"] = np.array(json_data["level_heights"], dtype=np.float64)
    volcano_altitude = json_data["volcano_altitude"]

    json_data["ordering_index"] = np.array(json_data["ordering_index"], dtype=np.int64)
    json_data["a_priori"] = np.array(json_data["a_priori_2d"], dtype=np.float64)
    json_data["a_posteriori"] = np.array(json_data["a_posteriori_2d"], dtype=np.float64)

    json_data["residual"] = np.array(json_data["residual"], dtype=np.float64)
    json_data["convergence"] = np.array(json_data["convergence"], dtype=np.float64)

    json_data["run_date"] = np.array(json_data["run_date"], dtype='datetime64[ns]')

    #Make JSON-data into 2d matrix
    json_data["a_posteriori"] = expandVariable(json_data["emission_times"], json_data["level_heights"], json_data["ordering_index"], json_data["a_posteriori"])
    json_data["a_priori"] = expandVariable(json_data["emission_times"], json_data["level_heights"], json_data["ordering_index"], json_data["a_priori"])

    #Prune any unused a priori elevations and timesteps
    if (prune):
        valid_elevations = max(np.flatnonzero((json_data['a_priori'].max(axis=1) + json_data['a_posteriori'].max(axis=1)) > prune_zero)) + 1
        valid_times = np.flatnonzero((json_data['a_priori'].max(axis=0) + json_data['a_posteriori'].max(axis=0)) > prune_zero)
        if valid_times_min is None:
            valid_times_min = min(valid_times)
        if valid_times_max is None:
            valid_times_max = max(valid_times) + 1

        json_data['a_priori'] = json_data['a_priori'][:valid_elevations,valid_times_min:valid_times_max]
        json_data['a_posteriori'] = json_data['a_posteriori'][:valid_elevations,valid_times_min:valid_times_max]
        json_data["ordering_index"] = json_data["ordering_index"][:valid_elevations,valid_times_min:valid_times_max]
        json_data["emission_times"] = json_data["emission_times"][valid_times_min:valid_times_max]
        json_data["level_heights"] = json_data['level_heights'][:valid_elevations]

    return json_data



def expandVariable(emission_times, level_heights, ordering_index, variable):
    #Make JSON-data into 2d matrix
    x = np.ma.masked_all(ordering_index.shape)
    for t in range(len(emission_times)):
        for a in range(len(level_heights)):
            emis_index = ordering_index[a, t]
            if (emis_index >= 0):
                x[a, t] = variable[emis_index]
    return x



def saveFig(filename, fig, metadata):
    with PdfPages(filename) as pdf:
        pdf.attach_note(metadata, positionRect=[0, 0, 100, 100])
        pdf.savefig(fig, bbox_inches='tight', pad_inches=0)
        
        
def getColorMap(colormap, bins=256):
    #If we already have a colormap
    if (not isinstance(colormap, str)):
        return colormap

    colors = [
        (0.0, (1.0, 1.0, 0.8)),
        (0.05, (0.0, 1.0, 0.0)),
        (0.4, (0.9, 1.0, 0.2)),
        (0.6, (1.0, 0.0, 0.0)),
        (1.0, (0.6, 0.2, 1.0))
    ]
    if (colormap == 'default'):
        pass
    elif (colormap == 'ippc'):
        colors = [
            (0.0/4, (1.0, 1.0, 1.0)), #0-0.2 g/m2 white
            (0.2/4, (0.498, 0.996, 0.996)), #0.2-2.0 g/m2 turquoise
            (2.0/4, (0.573, 0.58, 0.592)), #2.0-4.0 g/m2 gray
            (4.0/4, (0.875, 0.012, 0.012)) # >4.0 g/m2 red
        ]
        bins = 5
    elif (colormap == 'alternative'):
        colors = [
            (0.0, (1.0, 1.0, 0.6)),
            (0.4, (0.9, 1.0, 0.2)),
            (0.6, (1.0, 0.8, 0.0)),
            (0.7, (1.0, 0.4, 0.0)),
            (0.8, (1.0, 0.0, 0.0)),
            (0.9, (1.0, 0.2, 0.6)),
            (1.0, (0.6, 0.2, 1.0))
        ]
    elif (colormap == 'birthe'):
        colors = [
            ( 0/35, ("#ffffff")),
            ( 4/35, ("#b2e5f9")),
            (13/35, ("#538fc9")),
            (18/35, ("#47b54c")),
            (25/35, ("#f5e73c")),
            (35/35, ("#df2b24"))
        ]
    elif (colormap == 'stohl'):
        colors = [
            ( 0.00/10, ("#ffffff")),
            ( 0.35/10, ("#ffe5e2")),
            ( 0.60/10, ("#b1d9e6")),
            ( 1.00/10, ("#98e8a8")),
            ( 2.00/10, ("#fffc00")),
            ( 5.00/10, ("#ff0d00")),
            (10.00/10, ("#910000"))
        ]
    else:
        # Assume this is a standard matplotlib colormap name
        return colormap
        
    cm = LinearSegmentedColormap.from_list('ash', colors, N=bins)
    cm.set_bad(alpha = 0.0)

    return cm
    
def npTimeToDatetime(np_time):
    return datetime.datetime.utcfromtimestamp((np_time - np.datetime64('1970-01-01T00:00')) / np.timedelta64(1, 's'))

def npTimeToStr(np_time, fmt="%Y-%m-%d %H:%M"):
    return npTimeToDatetime(np_time).strftime(fmt)

def plotEmissions(json_data,
                dataset,
                colormap='default',
                unit='Tg',
                axis_date_format="%d %b\n%H:%M",
                y_max=None,
                usetex=True,
                plotsum=True,
                **kwargs,
            ):

    #Create x ticks and y ticks
    x_ticks = np.arange(0, json_data['emission_times'].size)
    x_labels = [npTimeToStr(t, fmt=axis_date_format) for t in json_data['emission_times']]
    y_ticks = np.arange(-0.5, json_data['level_heights'].size+0.5)
    y_labels = ["{:.0f}".format(a) for a in np.cumsum(np.concatenate(([json_data['volcano_altitude']], json_data['level_heights'])))]

    #Subsample x ticks / y ticks
    #x_ticks = x_ticks[2::48]
    #x_labels = x_labels[2::48]
    x_ticks = x_ticks[3::8]
    x_labels = x_labels[3::8]
    y_ticks = y_ticks[::2]
    y_labels = y_labels[::2]
    
    if (y_max is None):
        y_max = max(1.0e-10, 1.3*dataset.sum(axis=0).max())

    plotargs = {
        'aspect': 'auto', 
        'interpolation': 'none',
        'origin': 'lower', 
        'cmap': getColorMap(colormap)
    }
    plotargs.update(**kwargs)

    if len(y_labels) > 1 :
        plt.imshow(dataset, **plotargs)
        cbar = plt.colorbar(orientation='horizontal', pad=0.15, label=unit)
        plt.xticks(ticks=x_ticks, labels=x_labels, rotation=0, horizontalalignment='center', usetex=usetex)
        plt.yticks(ticks=y_ticks, labels=y_labels, usetex=usetex)
    else:
        # no height
        x_vals = [npTimeToDatetime(t) for t in json_data['emission_times']]
        sum = dataset.sum()
        sum_unit = unit
        # hardcoded units
        if unit == 'g/s':
            sum *= 3600 / (1000)
            sum_unit = "kg"
        elif unit == 'PBq/h':
            sum_unit = 'PBq'
        elif unit == 'Bq/h':
            sum_unit = 'PBq'
            sum *= 1.e-15
        elif unit == 'Bq/s': # ruthenium
            sum_unit = 'TBq'
            sum *= 3600 * 1.e-12

        plt.plot(x_vals, dataset[0], label=f'Sum: {sum:.0f} {sum_unit}')
        plt.xticks(rotation=40)
        plt.legend()

    if (plotsum):
        plt.sca(plt.gca().twinx())
        plt.autoscale(False)
        plt.plot(dataset.sum(axis=0), 'k--', linewidth=2, alpha=0.5, label='Sum')
        plt.ylim(0, y_max)
        plt.grid()
        plt.legend()
        

def plotAshInv(json_data,
                unit="Tg",
                colormap='default',
                usetex=True,
                plotsum=True,
                orientation='vertical',
                axis_date_format="%d %b\n%H:%M",
                dpi=200,
                fig_width=6,
                fig_height=4,
                vmin=0,
                vmax=None,
                plot_a_priori=False,
                plot_a_posteriori=True,
                plot_difference=False,
                plot_residual=True,
                **kwargs):

    nfigs=0
    if (plot_a_priori): nfigs += 1
    if (plot_a_posteriori): nfigs += 1
    if (plot_difference): nfigs += 1
    if (plot_residual): nfigs += 1
    
    if (orientation == 'horizontal'):
        fig, axs = plt.subplots(nrows=1, ncols=nfigs, figsize=(nfigs*fig_width,fig_height), dpi=dpi)
    elif (orientation == 'vertical'):
        fig, axs = plt.subplots(nrows=nfigs, ncols=1, figsize=(fig_width,nfigs*fig_height), dpi=dpi)

    if (nfigs == 1):
        axs = [axs]
    
    unit_scale = 0.0
    if (unit == 'Tg'):
        unit_scale = 1.0
    elif (unit == 'kg/(m*s)'):
        # The setup is to emit 1 tg over three hours for each level
        # Converting this to kg / (m * s)
        duration = np.diff(json_data['emission_times'])/np.timedelta64(1, 's')
        assert(np.all(duration == duration[0]))
        duration = duration[0]

        unit_scale = 1.0/(json_data['level_heights'][:,None]*duration)*1.0e9
    elif (unit == 'g/s'): # etex
        unit_scale = 1.0
    elif unit == 'PBq/h': # loviisa
        unit_scale = 1.0
    elif unit == 'Bq/h': # loviisa2
        unit_scale = 1.0
    elif unit == 'Bq/s': # ruth
        unit_scale = 1.0
    else:
        raise "Unknown unit {:s}".format(unit)
        
        
    

    y_max = max(1.0e-10, 1.3*max((unit_scale*json_data['a_priori']).sum(axis=0).max(), (unit_scale*json_data['a_posteriori']).sum(axis=0).max()))

    if (vmax is None):
        vmax = max((unit_scale*json_data['a_priori']).max(), (unit_scale*json_data['a_posteriori']).max())

    fig_ctr = 0

    # First subfigure (a priori)
    if (plot_a_priori):
        plt.sca(axs[fig_ctr])
        plt.title("A priori ({:s})".format(unit))
        plotEmissions(json_data, unit_scale*json_data['a_priori'], 
            unit=unit, 
            colormap=colormap, 
            axis_date_format=axis_date_format, 
            vmin=vmin,
            vmax=vmax, 
            y_max=y_max,
            plotsum=plotsum, 
            usetex=usetex)
        fig_ctr += 1

    #Second subfigure (a posteriori)
    if (plot_a_posteriori):
        plt.sca(axs[fig_ctr])
        plt.title("A posteriori ({:s})".format(unit))
        plotEmissions(json_data, unit_scale*json_data['a_posteriori'], 
            unit=unit, 
            colormap=colormap, 
            axis_date_format=axis_date_format, 
            vmin=vmin,
            vmax=vmax, 
            y_max=y_max,
            plotsum=plotsum, 
            usetex=usetex)
        fig_ctr += 1

    #Third subfigure (difference)
    if (plot_difference):
        plt.sca(axs[fig_ctr])
        plt.title("(Inverted - A priori) / A priori")
        norm = TwoSlopeNorm(vmin=-1.0, vcenter=0, vmax=2)
        #norm = SymLogNorm(linthresh=0.1, vmin=-1.0, vmax=r_vmax, base=10)
        #norm = MidpointLogNorm(lin_thres=0.01, lin_scale=1.0, vmin=-1.0, vmax=10, base=10)
        diff = (json_data['a_posteriori']-json_data['a_priori']) / json_data['a_priori']
        plotEmissions(json_data, diff, 
            unit='Tg', 
            colormap='bwr', 
            axis_date_format=axis_date_format, 
            y_max=y_max,
            plotsum=False, 
            usetex=usetex,
            norm=norm,
            vmin=-1,
            vmax=2)
        fig_ctr += 1

    #Fourth subfigure (convergence)
    if (plot_residual):
        plt.sca(axs[fig_ctr])
        plt.title("Convergence / residual")
        plt.plot(json_data['convergence'], 'r-', linewidth=2, label='Convergence')
        plt.xlabel("Iteration")

        plt.sca(axs[1].twinx())
        plt.plot(json_data['residual'], 'b-', linewidth=2, label='Residual')
        plt.xlabel("Iteration")

        plt.legend()

        fig_ctr += 1


    #Set tight layout to minimize overlap
    plt.tight_layout()
    #plt.subplots_adjust(top=0.9)

    return fig, axs





def downsample(arr, target, rebin_type='median'):
    """ Resizes an image to something close to target """

    def prime_factors(n):
        """ Finds prime factors of n  """
        i = 2
        factors = []
        while i * i <= n:
            if (n % i) != 0:
                i += 1
            else:
                n = n // i
                factors.append(i)
        if n > 1:
            factors.append(n)
        return factors

    def find_downsample_factor(shape, output):
        """ Finds a downsample factor so that shape is "close" to output """
        factors = prime_factors(int(shape))
        factor = 1
        for f in factors:
            if ((shape / (factor*f)) > output):
                factor *= f
            else:
                break
        return factor

    def rebin(arr, new_shape, rebin_type):
        """Rebin 2D array arr to shape new_shape by averaging."""
        if (new_shape[0] < arr.shape[0] or new_shape[1] < arr.shape[1]):
            shape = (new_shape[0], arr.shape[0] // new_shape[0],
                    new_shape[1], arr.shape[1] // new_shape[1])
            if (rebin_type == 'mean'):
                return arr.reshape(shape).mean(-1).mean(1)
            elif (rebin_type == 'median'):
                return np.median(np.median(arr.reshape(shape), axis=-1), axis=1)
            elif (rebin_type == 'max'):
                return arr.reshape(shape).max(-1).max(1)
            elif (rebin_type == 'min'):
                return arr.reshape(shape).min(-1).min(1)
        else:
            return arr

    target_size = [s // find_downsample_factor(s, t) for s, t in zip(arr.shape, target)]
    return rebin(arr, target_size, rebin_type)


def plotAshInvMatrix(matrix, fig=None, do_downsample=True, rebin_type='median'):
    if (fig is None):
        fig = plt.figure(figsize=(18, 18))


    #Downsample M to make (much) faster to plot...
    fig_size = fig.get_size_inches()*fig.dpi
    vmin = max(matrix.min(), 1e-10)
    vmax = max(matrix.max(), 2e-10)
    extent = [0, matrix.shape[1], matrix.shape[0], 0]

    m = matrix
    if (do_downsample):
        m = downsample(matrix, fig_size, rebin_type)

    #For plotting, force negative numbers to zero
    m[m<0] = 0.0

    plt.imshow(m,
        aspect='auto',
        interpolation='none',
        norm=LogNorm(vmin=vmin, vmax=vmax),
        extent=extent)
    plt.title('Matrix')
    plt.colorbar()
    plt.xlabel('Emission number')
    plt.ylabel('Observation number')

    return fig


if __name__ == "__main__":
    import configargparse

    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    parser = configargparse.ArgParser(description='Plot from ash inversion.')
    parser.add("-j", "--json", type=str, help="JSON-file to plot", required=True)
    parser.add("-o", "--output", type=str, help="Output file")
    parser.add("--unit", type=str, help="Unit to use for plots ({Tg|kg/(m*s)}")
    parser.add("--colormap", type=str, help="Colormap to use")
    parser.add("--usetex", type=str2bool, help="Use latex", nargs='?', const=True, default=True)
    parser.add("--plotsum", type=str2bool, help="Plot sum of emitted ash")
    parser.add("--prune", type=str2bool, help="Prune empty elevations")
    parser.add("--orientation", type=str, help="Orientation of figures (vertical|horizontal)")
    parser.add("--axis_date_format", type=str, help="Date format for axis")
    parser.add("--dpi", type=int, help="Dots per inch")
    parser.add("--fig_width", type=float, help="Width of each subfigure")
    parser.add("--fig_height", type=float, help="Height of each subfigure")
    args = parser.parse_args()

    print("Arguments: ")
    print("=======================================")
    for var, val in vars(args).items():
        print("{:s} = {:s}".format(var, str(val)))
    print("=======================================")

    outfile = args.output
    if outfile is None:
        basename, ext = os.path.splitext(os.path.abspath(args.json))
        outfile = basename + ".pdf"

    if args.usetex:
        plt.rc('font',**{'family':'serif','serif':['Times']})
        plt.rc('text', usetex=True)

    print("Writing output to " + outfile)
    json_file = args.json
    args = {k: v for k, v in vars(args).items() if v is not None}
    makePlotFromJson(json_file, outfile, **args)

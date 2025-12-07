import pickle
import numpy as np
import pandas as pd
import json
import re
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from .profiles import *
from .emissions import *

class EmissionScenario():
    def __init__(self,type_of_emission):
        self.profiles = []
        self.__is_divided_by_dh = False
        self.__is_normalized_by_total_mass = False
        self.__is_height_adjusted = False
        #self.__is_time_adjusted = False

        if (isinstance(type_of_emission, Emission) == False):
            raise TypeError("type_of_emission must be an instance of Emission")
        
        self.type_of_emission = type_of_emission

    def add_profile(self, profile: VerticalProfile):
        if isinstance(profile, VerticalProfile):
            self.profiles.append(profile)
        else:
            raise TypeError("Profile must be an instance of VerticalProfile")

    def __list_profiles(self):
        heights_on_levels=self.profiles[0].h
        scenario_2d_array=np.array([profile.values for profile in self.profiles]).T
        
        for j in np.arange(len(heights_on_levels)-1,-1,-1):
	        self.__print_vector(scenario_2d_array[j,:],sep=' ',f='{:0.6e}')
        
        return [profile.__class__.__name__ for profile in self.profiles]

    def getNumberOfProfiles(self):
        return len(self.profiles)

    def _clear_profiles(self):
        self.profiles = []

    #def getProfiles(self):
    #    for p in self.profiles:
    #        yield p

    def __repr__(self):
        return f"EmissionScenario(profiles={self.__list_profiles()})"
    
    def __print_vector(self,vector,sep=' ',f="{:0.6e}"):
        print((sep.join(f.format(x) for x in vector)))
    
    #returns start time of eruption.
    def getStartDateTime(self):
        return self.profiles[0].start_datetime

    #returns end time of eruption.
    def getEndDateTime(self):
        return self.profiles[-1].start_datetime + timedelta(seconds=int(self.profiles[-1].duration_sec))

    def get_emitted_mass_within(self, time_limit):
        """
        Estimate emitted mass (Mt) from start until a cutoff.
        time_limit can be hours (int/float), a timedelta, or an absolute datetime.
        Returns a formatted string with units (e.g., "0.300 Mt").
        """
        if len(self.profiles) == 0:
            return "0.000 Mt"

        if isinstance(time_limit, (int, float)):
            cutoff = self.getStartDateTime() + timedelta(hours=float(time_limit))
        elif isinstance(time_limit, timedelta):
            cutoff = self.getStartDateTime() + time_limit
        elif isinstance(time_limit, datetime):
            cutoff = time_limit
        else:
            raise TypeError("time_limit must be hours (int/float), timedelta, or datetime")

        # Work with un-normalized profile masses, then scale to prescribed emission mass
        total_unscaled = 0.0
        partial_unscaled = 0.0
        for profile in self.profiles:
            start = profile.start_datetime
            duration_sec = int(getattr(profile, "duration_sec", 0))
            # Zero-duration profiles contribute nothing; skip to avoid divide-by-zero.
            if duration_sec <= 0:
                continue
            end = start + timedelta(seconds=duration_sec)
            mass = profile.getProfileEmittedMass()

            if end <= cutoff:
                partial_unscaled += mass
            elif start < cutoff:
                overlap_frac = (cutoff - start).total_seconds() / duration_sec
                partial_unscaled += mass * overlap_frac
            else:
                # starts after cutoff; no contribution
                pass

            total_unscaled += mass

        if total_unscaled == 0.0:
            return "0.000 Mt"

        # Scale partial sum so full scenario equals type_of_emission.mass_Mt
        scale = self.type_of_emission.mass_Mt / total_unscaled
        mass_mt = partial_unscaled * scale
        return f"{mass_mt:.3f} Mt"
    
    def get_profiles_Decimal_StartTimeAndDuration(self):
        start_times = []
        duration_mins = []
        for profile in self.profiles:
            s,d = profile.getProfileStartTimeAndDuration()
            start_times.append(s)
            duration_mins.append(d)
        
        return start_times,duration_mins
    
    def get_profiles_StartDateTime(self):
        return [profile.start_datetime for profile in self.profiles]
    
    def getScenarioEmittedMass(self):
        return np.sum([profile.getProfileEmittedMass() for profile in self.profiles])

    def __scaleProfiles(self, scale):
        for profile in self.profiles:
            profile.values = profile.values * scale

    def normalize_by_total_mass(self):
        mass_before=self.getScenarioEmittedMass()
        scale = self.type_of_emission.mass_Mt/mass_before
        self.__scaleProfiles(scale)
        mass_after=self.getScenarioEmittedMass()
        print(f'\n{self.type_of_emission.get_name_of_material()} mass before: \
              {mass_before:.3f} Mt, and after: {mass_after:.3f} Mt normalisation')
        
        self.__is_normalized_by_total_mass = True
    
    def plot_profiles(self,*args, **kwargs):
        scale_factor=2000.0#*1000.0
        
        if (self.__is_divided_by_dh):
            scale_factor = scale_factor * 1000.0    #for conviniency
        
        hours=[profile.hour for profile in self.profiles]
        fig = plt.figure(figsize=(18,7))
        for i, profile in enumerate(self.profiles):
            x_values = scale_factor * profile.values + profile.hour
            y_values = profile.h / 1000.0
            plt.plot(x_values, y_values, *args, **kwargs)
        
        plt.ylim(0.0, 40)
        #plt.xlim(0.0,0.03)
        plt.ylabel('Altitude, $km$')
        plt.xlabel('Decimal hour')

        plt.axhline(y=16.5, linestyle=':',color='black',linewidth=1.0)
        plt.gca().yaxis.set_major_locator(plt.MultipleLocator(5))
        plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))
        plt.xticks(hours)
       
        plt.title(self)
        
        plt.grid(True,alpha=0.3)
        plt.show()
  
    def __getColorMap(self,colormap = 'stohl', bins=256):
        #taken from https://github.com/metno/VolcanicAshInversion/
        
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
  
    def plot(self,*args, **kwargs):
        scenario_2d_array = np.array([profile.values for profile in self.profiles]).T
        h_centers = self.profiles[0].h / 1000.0
        times = [profile.start_datetime for profile in self.profiles]
        durations_sec = [int(getattr(profile, 'duration_sec', 0)) for profile in self.profiles]

        # If the last interval has zero duration (common sentinel), drop it from plot
        if len(durations_sec) > 0 and durations_sec[-1] == 0:
            scenario_2d_array = scenario_2d_array[:, :-1]
            times = times[:-1]
            durations_sec = durations_sec[:-1]

        # Build time edges from start times and durations so each column spans its interval
        time_edges = [times[0]]
        for i in range(len(times)):
            time_edges.append(times[i] + timedelta(seconds=durations_sec[i]))

        # Build vertical edges from level centers
        if len(h_centers) >= 2:
            dh = np.diff(h_centers)
            y_edges = np.empty(len(h_centers) + 1, dtype=h_centers.dtype)
            y_edges[1:-1] = h_centers[:-1] + 0.5 * dh
            y_edges[0] = h_centers[0] - 0.5 * (h_centers[1] - h_centers[0])
            y_edges[-1] = h_centers[-1] + 0.5 * (h_centers[-1] - h_centers[-2])
            y_edges[0] = max(0.0, y_edges[0])
        else:
            # Single level fallback
            y_edges = np.array([max(0.0, h_centers[0] - 0.5), h_centers[0] + 0.5])

        fig = plt.figure(figsize=(14, 7))
        plt.pcolormesh(time_edges, y_edges, scenario_2d_array, alpha=0.08, zorder=2, facecolor='none', edgecolors='grey', linewidths=0.01)
        cs = plt.pcolormesh(time_edges, y_edges, scenario_2d_array, cmap=self.__getColorMap())
        
        # Store colorbar range if not already set
        if not hasattr(self, "_colorbar_range"):
            self._colorbar_range = (np.nanmin(scenario_2d_array), np.nanmax(scenario_2d_array))
        # Apply stored colorbar range
        #cs.set_clim(*self._colorbar_range)
        plt.colorbar(cs, label='Emissions')

        plt.ylim(0.0, 40)
        plt.ylabel('Altitude, $km$')
        plt.xlabel('Time')
        
        # Place ticks on interval edges for clarity
        times_with_minutes = [dt.strftime('%H:%M') for dt in time_edges]
        plt.xticks(time_edges, times_with_minutes, rotation=90, fontsize=6)

        plt.axhline(y=16.5, linestyle=':',color='black',linewidth=1.0)
        plt.gca().yaxis.set_major_locator(plt.MultipleLocator(5))
        plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))

        # Duplicate y ticks and labels on the right-hand side for clarity
        ax = plt.gca()
        ax_right = ax.twinx()
        # Ensure identical limits and ticks
        ax_right.set_ylim(ax.get_ylim())
        ax_right.set_yticks(ax.get_yticks())
        # Copy tick labels text from left axis
        ax_right.set_yticklabels([t.get_text() for t in ax.get_yticklabels()])
        # Copy locators so major/minor ticks match
        try:
            ax_right.yaxis.set_major_locator(ax.yaxis.get_major_locator())
            ax_right.yaxis.set_minor_locator(ax.yaxis.get_minor_locator())
        except Exception:
            pass
        # Do not copy the y-axis label to the right side (keep only ticks/labels)
        ax_right.set_ylabel('')

        # Set x-axis limits: lower - round down to nearest day, upper - round up to next day
        min_time = time_edges[0].replace(hour=0, minute=0, second=0, microsecond=0)
        max_time = (time_edges[-1] + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        plt.xlim(min_time, max_time)
        #plt.tight_layout()
        plt.title(self)
        plt.show()
  
    def __str__(self):
        s = self.__class__.__name__+" "+f'{self.getNumberOfProfiles()} profiles. {self.type_of_emission}. \
        \nStart time: {self.getStartDateTime()} End time: {self.getEndDateTime()}. '
        
        if (self.__is_divided_by_dh):
            if (self.__is_normalized_by_total_mass):
                return s +  f'Units [Mt/m/sec]. Normalized by total mass = {self.getScenarioEmittedMass():.2f} Mt'
            else:
                return s + 'Units [Mt/m/sec]'
        else:
            return s + 'Units [Mt/sec]'

    def __resample_emissions(self,emissions, durations, regular_dt):
        t_end = np.sum(durations)
        original_times = np.concatenate(([0], np.cumsum(durations)))

        cumulative_mass = np.zeros_like(original_times, dtype=float)
        for i in range(len(emissions)):
            cumulative_mass[i+1] = cumulative_mass[i] + emissions[i] * durations[i]

        new_times = np.arange(0, t_end + regular_dt, regular_dt)
        new_cumulative_mass = np.interp(new_times, original_times, cumulative_mass)
        new_emissions = np.diff(new_cumulative_mass) / regular_dt

        #check the mass balance
        if np.abs(np.sum(new_emissions) * regular_dt - np.sum(emissions * durations)) > 1e-6:
            raise ValueError("Mass balance error: the total mass before and after resampling does not match.")
        #sum(new_emissions*regular_dt)
        #sum(durations*emissions[:-1])
        
        #return new_times[:-1], new_emissions, original_times
        return new_emissions

    def interpolate_time(self, interval_minutes=60):
        StartDateTime = self.getStartDateTime()
        # Round minutes to nearest 10th
        start_minute = round(StartDateTime.minute / 10.0) * 10.0
        StartDateTime_rounded = StartDateTime.replace(minute=0, second=0) + timedelta(minutes=start_minute)

        new_datetime_list = pd.date_range(start=StartDateTime_rounded, end=self.getEndDateTime(), 
                           freq=pd.Timedelta(days=0, hours=0, minutes=interval_minutes))

        #Generate new dates based on the new hours, keep h the same
        levels_h = self.profiles[0].h     
        new_years = new_datetime_list.year.tolist()
        new_months = new_datetime_list.month.tolist()
        new_days = new_datetime_list.day.tolist()
        new_hours = new_datetime_list.hour.tolist()
        new_minutes = new_datetime_list.minute.tolist()
        new_duration_hours = np.diff(new_datetime_list)/ np.timedelta64(1, 'h')
        new_duration_hours = np.append(new_duration_hours,0)

        temp_scenario_2d_array = np.array([profile.values for profile in self.profiles]).T
        temp_interp_solution_emission_scenario = np.zeros([temp_scenario_2d_array.shape[0],len(new_datetime_list)])
        
        old_durations_seconds = np.array([profile.duration_sec for profile in self.profiles], dtype=int) 

        # Resample
        for i in range(temp_interp_solution_emission_scenario.shape[0]):
            emissions = temp_scenario_2d_array[i, :]
            if (sum(emissions) == 0):
                continue
            
            new_emissions = self.__resample_emissions(emissions, old_durations_seconds, interval_minutes * 60)
            
            # Pad new_emissions with zeros on the right to match the shape of the new emission scenario
            if new_emissions.shape[0] < temp_interp_solution_emission_scenario[i, :].shape[0]:
                pad_width = temp_interp_solution_emission_scenario[i, :].shape[0] - new_emissions.shape[0]
                new_emissions = np.pad(new_emissions, (0, pad_width), mode='constant')
            
            temp_interp_solution_emission_scenario[i, :] = np.maximum(new_emissions, 0)
        
        # Clear existing profiles
        self._clear_profiles() 
        
        # Add new profiles with interpolated values at new time points. -1 because last time is the time, when eruption is finished.
        for i in range(temp_interp_solution_emission_scenario.shape[1]):
            p=VerticalProfile(levels_h,temp_interp_solution_emission_scenario[:,i],new_years[i],
                                            new_months[i],new_days[i],new_hours[i]+new_minutes[i]/60.0,new_duration_hours[i] * 3600)
            p.setDatetime(new_datetime_list[i])
            self.add_profile(p)

        #zero emissions for last profile
        self.profiles[-1].values *=0
        self.profiles[-1].erup_beg=0

        #self.__is_time_adjusted = True

    def interpolate_height(self,new_height):        
        #if (self.__is_time_adjusted == False):    
        #    raise ValueError('Time must be adjusted before adjusting height')
        
        if not isinstance(new_height, np.ndarray):
            raise TypeError("new_height must be a numpy array")
        
        if len(new_height) < 2:
            raise ValueError("new_height must contain at least two elements")

        if(np.all(new_height[1:] > new_height[:-1])==False):
            raise ValueError('new_height must be monotonically increasing')
        
        for profile in self.profiles:
            profile.interpoloate_height(new_height)
        
        self.__is_height_adjusted = True
    
    def divide_by_dh(self,dh):        
        if (self.__is_height_adjusted == False):
            raise ValueError('Height must be adjusted before dividing by dh')
        
        for profile in self.profiles:
            profile.values = profile.values / dh
            profile.is_divided_by_dh = True
            profile.dh = dh
        
        self.__is_divided_by_dh = True

    def set_values_by_criteria(self, value, time_start=None, time_end=None,
                               height_min_m=None, height_max_m=None,
                               height_above_m=None, height_below_m=None,
                               condition_func=None, debug=False):
        """
        Set emission values on the scenario according to simple criteria or a custom function.

        Parameters
        - value: numeric value to set where the condition matches.
        - time_start, time_end: optional. If provided, restrict to profiles whose
          `start_datetime` falls within the interval. These may be:
            * datetime.datetime objects (full-date comparison), or
            * strings 'HH:MM' which will be treated as time-of-day comparisons
              (applied to each profile's time-of-day), or
            * pandas.Timestamp strings parseable by `pd.to_datetime`.
        - height_min_m, height_max_m: restrict to heights between these (meters, inclusive).
        - height_above_m / height_below_m: convenience single-sided bounds (meters).
        - condition_func: optional callable(height_m, profile_datetime) -> bool.
          If provided, it overrides the simple criteria and is used to decide
          whether to set the cell to `value`.

        Examples:
          - set 1 everywhere between 10:00 and 12:00 at heights 3000-4000 m:
              scen.set_values_by_criteria(1, time_start='10:00', time_end='12:00', height_min_m=3000, height_max_m=4000)
          - set 0 above 15000 m:
              scen.set_values_by_criteria(0, height_above_m=15000)
          - use a custom callable:
              scen.set_values_by_criteria(5, condition_func=lambda h, dt: (h>5000 and dt.hour==14))
        """

        # Helper to parse time params
        def _parse_time_param(param):
            if param is None:
                return None

            # numpy.datetime64 -> convert to python datetime
            if isinstance(param, np.datetime64):
                return ('datetime', pd.to_datetime(param).to_pydatetime())

            # If it's a string that matches HH:MM or HH:MM:SS, treat it as time-of-day
            if isinstance(param, str):
                if re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', param.strip()):
                    try:
                        t = pd.to_datetime(param, format='%H:%M').time()
                        return ('time_of_day', t)
                    except Exception:
                        try:
                            t = pd.to_datetime(param, format='%H:%M:%S').time()
                            return ('time_of_day', t)
                        except Exception:
                            pass

            # try pandas to_datetime to get a full datetime (handles ISO strings, pandas.Timestamp, etc.)
            try:
                dt = pd.to_datetime(param)
                return ('datetime', dt.to_pydatetime())
            except Exception:
                raise TypeError(f"Could not parse time parameter: {param}")

        ts_parsed = _parse_time_param(time_start)
        te_parsed = _parse_time_param(time_end)

        if debug:
            print(f"[set_values_by_criteria] parsed time_start={ts_parsed}, time_end={te_parsed}")

        # iterate through profiles and heights
        for profile in self.profiles:
            prof_dt = profile.start_datetime
            # Determine whether this profile passes time filters
            time_ok = True
            if ts_parsed is not None or te_parsed is not None:
                # If both are time-of-day, compare only time-of-day (preserve previous behaviour)
                if ts_parsed and ts_parsed[0] == 'time_of_day' and te_parsed and te_parsed[0] == 'time_of_day':
                    start_t = ts_parsed[1]
                    end_t = te_parsed[1]
                    cur_t = prof_dt.time()
                    # handle wrap-around (e.g., 23:00-02:00)
                    if start_t <= end_t:
                        time_ok = (start_t <= cur_t <= end_t)
                    else:
                        time_ok = (cur_t >= start_t or cur_t <= end_t)
                else:
                    # For mixed or full-datetime inputs, compare full datetimes.
                    # Anchor any time-of-day values to the profile's date.
                    def _to_dt(parsed):
                        if parsed is None:
                            return None
                        if parsed[0] == 'datetime':
                            return parsed[1]
                        # time_of_day: combine with profile date
                        if parsed[0] == 'time_of_day':
                            return datetime(prof_dt.year, prof_dt.month, prof_dt.day,
                                            parsed[1].hour, parsed[1].minute, parsed[1].second)
                        return None

                    ts_dt = _to_dt(ts_parsed)
                    te_dt = _to_dt(te_parsed)

                    # If both datetimes are present, handle wrap-around where end <= start
                    if ts_dt is not None and te_dt is not None:
                        if te_dt < ts_dt:
                            # assume end is on the next day
                            te_dt = te_dt + timedelta(days=1)
                        time_ok = (ts_dt <= prof_dt <= te_dt)
                    else:
                        # Only start or only end provided
                        if ts_dt is not None:
                            time_ok = (prof_dt >= ts_dt)
                        if te_dt is not None:
                            time_ok = (prof_dt <= te_dt)

            if not time_ok:
                if debug:
                    print(f"[set_values_by_criteria] profile {profile} at {prof_dt} skipped by time filter")
                continue

            # Now loop over heights within this profile
            for idx, h in enumerate(profile.h):
                height_ok = True
                if height_min_m is not None and h < height_min_m:
                    height_ok = False
                if height_max_m is not None and h > height_max_m:
                    height_ok = False
                if height_above_m is not None and h <= height_above_m:
                    height_ok = False
                if height_below_m is not None and h >= height_below_m:
                    height_ok = False

                if not height_ok:
                    if debug:
                        print(f"[set_values_by_criteria] profile {profile} at {prof_dt} height {h} skipped by height filter")
                    continue

                # If a custom callable is provided, it overrides the simple criteria
                if condition_func is not None:
                    try:
                        do_set = bool(condition_func(h, prof_dt))
                    except Exception as e:
                        raise RuntimeError(f"condition_func raised an exception: {e}") from e
                    if do_set:
                        if debug:
                            print(f"[set_values_by_criteria] setting profile {profile} at {prof_dt} height {h} -> {value} (by condition_func)")
                        profile.values[idx] = value
                else:
                    # All simple checks passed -> set value
                    if debug:
                        print(f"[set_values_by_criteria] setting profile {profile} at {prof_dt} height {h} -> {value}")
                    profile.values[idx] = value
        
class EmissionScenario_Inverted_Pinatubo(EmissionScenario):
    def __init__(self, type_of_emission, filename):
        super().__init__(type_of_emission)
        
        #staggerred_h is from the paper
        staggerred_h = np.array([91.56439, 168.86765, 273.9505, 407.21893, 574.90356, 788.33356, 1050.1624, 1419.9668, 
                            1885.3608, 2372.2937, 2883.3193, 3634.4663, 4613.3403, 5594.8545, 6580.381, 7568.5386, 
                            8558.1455, 9547.174, 10534.043, 11518.861, 12501.9375, 13484.473, 14454.277, 15393.3125, 
                            16300.045, 17189.598, 18083.797, 18998.496, 19939.57, 20905.723, 21890.363, 22886.46, 
                            23890.441, 24900.914, 25918.307, 26943.252, 27977.344, 29021.828, 30077.21, 31143.973, 
                            32221.8, 33310.13, 34408.86, 35517.9, 36637.133, 37766.45, 38905.723, 40054.82, 41213.594, 
                            42381.883, 43559.504, 44746.254, 45941.914, 47146.22])

        with open(filename,'rb') as infile:
            _,_,emission_scenario,years,months,days,hours,duration_sec,_ = pickle.load(infile,encoding='latin1')
        #emission_scenario in [Mt/sec]
        for i in range(emission_scenario.shape[1]):
            self.add_profile(VerticalProfile(staggerred_h,emission_scenario[:,i],years[i],
                                            months[i],days[i],hours[i],duration_sec[i]))

class EmissionScenario_Inverted_Eyjafjallajokull(EmissionScenario):
    def __init__(self, type_of_emission, json_filename):
        super().__init__(type_of_emission)
        
        json_data = self.__readJson(json_filename)
        years,months,days,hours = [],[],[],[]

        for ts in json_data['emission_times']:
            dt = pd.to_datetime(ts).to_pydatetime()
            years.append(dt.year)
            months.append(dt.month)
            days.append(dt.day)
            hours.append(dt.hour)
        
        #h - height of the levels
        h = np.array([a for a in np.cumsum(np.concatenate(([json_data['volcano_altitude']], json_data['level_heights'])))])
        #staggerred_h - height of the 'mass' points
        staggerred_h = h[0:-1] + 0.5 * json_data['level_heights']
        emission_scenario = np.array(json_data['a_posteriori'])
        
        emission_scenario *= 1e-9   #emission_scenario in [Mt/m/s] now
        self.__is_divided_by_dh = True
        for i in range(emission_scenario.shape[1]):
            self.add_profile(VerticalProfile(staggerred_h,emission_scenario[:,i],years[i],
                                            months[i],days[i],hours[i],3*60*60))

        #adding the last 'VerticalProfile_Zero'
        last_zero_profile_time = pd.to_datetime(json_data['emission_times'][-1]) + timedelta(seconds=3*60*60)
        self.add_profile(VerticalProfile_Zero(staggerred_h, last_zero_profile_time.year, 
                                              last_zero_profile_time.month,
                                              last_zero_profile_time.day, 
                                              last_zero_profile_time.hour, 3*60*60))

    def __expandVariable(self,emission_times, level_heights, ordering_index, variable):
        #Make JSON-data into 2d matrix
        x = np.ma.masked_all(ordering_index.shape)
        for t in range(len(emission_times)):
            for a in range(len(level_heights)):
                emis_index = ordering_index[a, t]
                if (emis_index >= 0):
                    x[a, t] = variable[emis_index]
        return x

    def __readJson(self,json_filename):
        #Read data
        with open(json_filename, 'r') as infile:
            json_string = infile.read()

        #Parse data
        json_data = json.loads(json_string)

        #Parse data we care about
        json_data["emission_times"] = np.array(json_data["emission_times"], dtype='datetime64[ns]')
        json_data["level_heights"] = np.array(json_data["level_heights"], dtype=np.float64)
        #volcano_altitude = json_data["volcano_altitude"]

        json_data["ordering_index"] = np.array(json_data["ordering_index"], dtype=np.int64)
        #json_data["a_priori"] = np.array(json_data["a_priori_2d"], dtype=np.float64)
        json_data["a_posteriori"] = np.array(json_data["a_posteriori_2d"], dtype=np.float64)


        #Make JSON-data into 2d matrix
        json_data["a_posteriori"] = self.__expandVariable(json_data["emission_times"], json_data["level_heights"], json_data["ordering_index"], json_data["a_posteriori"])
        #json_data["a_priori"] = expandVariable(json_data["emission_times"], json_data["level_heights"], json_data["ordering_index"], json_data["a_priori"])

        return json_data


class EmissionScenario_HayliGubbi(EmissionScenario):
    def __init__(self, type_of_emission, emissions_filename):
        super().__init__(type_of_emission)
        
        # Parse emissions file
        data = self.__parse_emission_file(emissions_filename)
        times_str = data['times']
        heights = data['heights']
        emissions = data['emissions']
        
        # Convert ISO 8601 time strings to datetime objects
        datetimes = [pd.to_datetime(t).to_pydatetime() for t in times_str]
        
        # Calculate duration between consecutive time points (in seconds)
        durations = []
        for i in range(len(datetimes) - 1):
            delta_sec = (datetimes[i + 1] - datetimes[i]).total_seconds()
            durations.append(delta_sec)
        # Last profile gets zero duration (sentinel)
        durations.append(0)
        
        # Create VerticalProfile for each time point
        for i, dt in enumerate(datetimes):
            emissions_at_time = emissions[:, i]
            profile = VerticalProfile(
                heights,
                emissions_at_time,
                dt.year,
                dt.month,
                dt.day,
                dt.hour + dt.minute / 60.0,
                durations[i]
            )
            profile.setDatetime(dt)
            self.add_profile(profile)
    
    def __parse_emission_file(self, filename):
        """
        Parse an emission text file with the following format:
        Row 1: 'time' followed by ISO 8601 datetime strings
        Row 2: 'height' followed by height values in meters
        Rows 3+: 2D array of emission values
        
        Returns a dictionary with keys 'times', 'heights', and 'emissions'
        """
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        # Parse time line (row 1)
        time_parts = lines[0].strip().split()
        times_str = time_parts[1:]  # Skip 'time' label
        
        # Parse height line (row 2)
        height_parts = lines[1].strip().split()
        heights = np.array([float(h) for h in height_parts[1:]], dtype=np.float64)  # Skip 'height' label
        
        # Parse emission data (rows 3+)
        emissions = []
        for i in range(2, len(lines)):
            row = lines[i].strip()
            if row:  # Skip empty lines
                values = np.array([float(v) for v in row.split()], dtype=np.float64)
                emissions.append(values)
        
        emissions = np.array(emissions)  # Shape: (num_heights, num_times)
        
        emissions = np.flipud(emissions) # Flip the 2D array vertically
        
        return {
            'times': times_str,
            'heights': heights,
            'emissions': emissions
        }
"""
Sputnik 2U Demo Power Visualizer Script

Author: Jacob Mukobi

Dependencies:

- Power budget spreadsheet: "power_budget.csv"
- Power generation plot file: "total_power_from_all_panels.h5"
- Thruster power plot file: "power_consumed_thruster_plot.h5"

- NumPy ("pip install numpy")
- matplotlib ("pip install matplotlib")
- tqdm ("pip install tqdm")
"""

#Imports

import numpy as np
import csv
import matplotlib.pyplot as plt
#import h5py
try:
    from tqdm import tqdm
    HasTqdm = True
except ImportError:
    print('''This program has a pretty loading bar for which you must have the tqdm package ("pip install tqdm"). It's really nice, so I highly reccomend it!''')
    HasTqdm = False


########################################### - SETUP - ##################################################


#Modifiers

TIME_STEP = 20              #Seconds
CONST_GENERATION = True     #Get power generation from simulation h5 file (False) or var GENERATION_VALUE (True)
CONST_THRUST = True         #Get thruster power draw from simulation h5 file (False) or var THRUST_POW (True)
CHECK_FOR_ECLIPSE = True    #Check if satellite is in eclipse and set power generation = 0
GET_SUN_POINTING = True     #Get sun pointing phases of maximum generation from spreadsheet
GENERATION_POW = 22.62      #Constant power generation value in Watts
MAX_GENERATION = 28.80
SIM_TIME = 478             #Length of simulation in minutes
ECLIPSE_START = 0           #Time that the first eclipse starts in minutes

#Orbital Parameters

#LTAN = 0                    #Longitude of the ascending node in hours
ALTITUDE = 550              #Altitude in km
EARTH_RAD = 6378100         #Radius of Earth in m
PERIOD = 95.6            #Orbital period in minutes

#Constants

BATTERY_CAPACITY = 36.5      #Total battery capacity in Watt hours
COMM_STRING = "Comms"       #Column zero value for communications row
BURN_STRING = "Burn"        #Column zero value for burn row
SUN_STRING = "Sun Pointing" #Column zero value for sun pointing phase
MAX_CHARGE_FRAC = .9        #Maximum charge state from 0-1
MIN_CHARGE_FRAC = .4        #Minimum charge state from 0-1
BATT_EFF = 0                #Battery efficiency in percent
CONVERTER_EFF = 0          #Converter efficiency in percent

#Files

USAGE_FILE = "power_budget.csv"
#GENERATION_FILE = "total_power_from_all_panels.h5"
#THRUST_FILE = "power_consumed_thruster_plot.h5"


########################################################################################################


#Get phases dictionary

phases = {}
labels = 0

with open(USAGE_FILE, 'r') as file:
        reader = csv.reader(file)

        for row in reader:
            try:
                start_time = float(row[1])*60
                try:
                    phases[row[0]].append(start_time)
                    labels += 1
                except KeyError:
                    phases.update({row[0]:[start_time]})
                    labels += 1

            except ValueError:
                pass 


#Find eclipse time

a = ALTITUDE*1000+EARTH_RAD
total_eclipse_angle = 2*np.degrees(np.arcsin(EARTH_RAD/a))
eclipse_time = (total_eclipse_angle/360)*PERIOD*60
daylight_time = PERIOD*60 - eclipse_time

"""
#Get power generation data from file

hf = h5py.File(GENERATION_FILE, "r")
n1 = hf.get("MC000000")
x_data = np.array(n1["xdata"])
y_data = np.array(n1["ydata"])

last_time = -1

gen_time = [0]
gen_value = [y_data[0]]

for i in range(len(x_data)):
    current_time = int(x_data[i])
    if current_time != last_time:
        gen_time.append(current_time)
        gen_value.append(y_data[i])

#Get thruster power data from file

hf = h5py.File(THRUST_FILE, "r")
n1 = hf.get("MC000000")
x_data = np.array(n1["xdata"])
y_data = np.array(n1["ydata"])

last_time = -1

thrust_time = [0]
thrust_value = [y_data[0]]

for i in range(len(x_data)):
    current_time = int(x_data[i])
    if current_time != last_time:
        thrust_time.append(current_time)

        thrust_value.append(-y_data[i])

        #TRYING TO BREAK IT
        
        if -y_data[i] > 0:
            thrust_value.append(60)
        else:
            thrust_value.append(-y_data[i])
        
        #END TRYING TO BREAK IT

#plt.plot(thrust_time, thrust_value)
#plt.show()

"""

#Initialize data lists and variables

batt_state = [BATTERY_CAPACITY*MAX_CHARGE_FRAC]
time = [0]
power_generated = [GENERATION_POW]
power_drawn = [0]

power_gen = GENERATION_POW
#thruster = 0
thrust_power = 0
if HasTqdm == True:
    loop = tqdm(total=SIM_TIME*60/TIME_STEP, position=0, leave=False)
time_in_sun = 0
time_in_eclipse = 0
InEclipse = False

#Loop through each timestep

for t in range(TIME_STEP, SIM_TIME*60, TIME_STEP):
    loop.set_description("Loading... ".format((t)))
    loop.update()
    IsComming = False
    IsBurning = False
    IsSunPointing = False

    with open(USAGE_FILE, 'r') as file:
        reader = csv.reader(file)

        #Check which phase of ConOps loop is currently in and take power data

        for row in reader:
            try:
                start_time = float(row[1])*60
                end_time = float(row[2])*60

                if start_time <= t and end_time >= t:
                    if row[0] == SUN_STRING:
                        IsSunPointing = True
                    else:
                        power_draw = float(row[4])
                        if row[0] == COMM_STRING:
                            IsComming = True
                        if row[0] == BURN_STRING:
                            IsBurning = True
                        else:
                            IsBurning = False
                    

            except ValueError:
                pass   
        
        """
        #Check for constant or simulated thruster power usage and generation
        
        if CONST_GENERATION == True:
            
        else:
            try:
                power_gen = gen_value[gen_time.index(t/60)]
                
            except ValueError:
                pass

        if CONST_THRUST == True:
            if IsBurning == True:
                thrust_power = THRUSTER_POW #float(row[30])
                print(row)
                print(thrust_power)
            else:
                thrust_power = 0
        else:
            try:
                thrust_power = thrust_value[thrust_time.index(t/60)]
                
            except ValueError:
                pass
        """

        power_gen = GENERATION_POW

        #Check for sun pointing

        if GET_SUN_POINTING == True:
            if IsSunPointing == True:
                power_gen = MAX_GENERATION
        
        #Check for eclipse

        if CHECK_FOR_ECLIPSE == True:
            if InEclipse == False:
                time_in_sun += TIME_STEP
                if time_in_sun >= daylight_time:
                    InEclipse = True
                    time_in_eclipse = 0
            else:
                time_in_eclipse += TIME_STEP
                power_gen = 0
                if time_in_eclipse >= eclipse_time:
                    InEclipse = False
                    time_in_sun = 0

        #Get total power usage and generation for current timestep

        

        if IsComming == True:
            thrust_power = 0
            #power_gen = 0

        power_draw += thrust_power

        power_generated.append(power_gen/(1+(BATT_EFF/100)))

        #print(power_draw)

        power_drawn.append(power_draw*(1+(CONVERTER_EFF/100)))

        #Iterate the battery state for current timestep

        new_batt_state = batt_state[len(batt_state)-1] + (power_gen/(1+(BATT_EFF/100)) - power_draw*(1+(CONVERTER_EFF/100)))*TIME_STEP/(60**2)

        #Check for overcharge and limit battery state

        if new_batt_state > BATTERY_CAPACITY*MAX_CHARGE_FRAC:
            new_batt_state = BATTERY_CAPACITY*MAX_CHARGE_FRAC

        #Append time step data to data lists

        batt_state.append(new_batt_state)
        time.append(t/60) 

loop.close()

#Create min and max charge bounding data

batt_max = []
batt_min = []

for step in time:
    batt_max.append(BATTERY_CAPACITY*MAX_CHARGE_FRAC)
    batt_min.append(BATTERY_CAPACITY*MIN_CHARGE_FRAC)

#Create plot

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(time, np.array(batt_max)*100/BATTERY_CAPACITY, color="mediumseagreen", ls="--", label="Max Charge (%)")
ax.plot(time, np.array(batt_min)*100/BATTERY_CAPACITY, color="indianred", ls="--", label="Max Discharge (%)")
ax.plot(time, np.array(batt_state)*100/BATTERY_CAPACITY,"b", label="Battery State (%)")

ax2 = ax.twinx()

ax2.plot(time, np.array(power_generated),"c", label="Power Input (W)")
ax2.plot(time, np.array(power_drawn),"m", label="Power Draw (W)")
plt.title("Battery SoC and Power Flux During ConOps")

ax2.set_ylim(0, 240)
ax.set_ylabel("Battery Charge State (%)")
ax2.set_ylabel("Power (W)")
ax.set_xlabel("Time (min)")
ax.set_yticks(np.arange(0, 100+1, 10))
ax.set_yticks(np.arange(0, 100+1, 2), minor = "True")
ax.grid(axis="y", which="major", alpha=.5)
ax.grid(axis="y", which="minor", alpha=.1)

legend_1 = ax.legend(loc=2)
legend_1.remove()
ax2.legend(loc=1)
ax2.add_artist(legend_1)

y = 115

for phase in phases:
    for time in phases[phase]:
        ax2.axvline(x = time/60, color = 'goldenrod', label = phase, zorder=-100, ls='--')
        if phase == "Starting Orbit":
            plt.text(time/60-17,y,phase,rotation=90)
        else:
            plt.text(time/60+2,y,phase,rotation=90)
        if y == 115:
            y = 150
        else:
            y = 115

plt.show()
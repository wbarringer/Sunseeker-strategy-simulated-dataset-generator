# Tools for generating a simulation dataset that can be used to test and train strategy software

# import random
import pyodbc
import json
import random


class Array:

    def __init__(self, cell_type="Max3", mode="Total_Area", area=4, cells=0, subs=2):
        if mode == "Total_Area":
            self.area = area  # Use a single value for the array area in m^2
        if mode == "Cell_Count":
            if cell_type == "Max3":
                self.area = cells * 0.15333  # Calculate array area based on the number of cells
            else:
                print("Unknown cell type, contact developer.")  # TODO add addition cell types if needed
        self.sub_arrays = subs  # number of sub-arrays
        if cell_type == "Max3":
            self.efficiency = 24.3

        # print("Array created")


class Battery:

    def __init__(self, series, parallel, capacity, max_v=4.2, nom_v=3.6, min_v=2.8, max_i=1, min_i=-1, avg_z=.034):
        self.series = series
        self.parallel = parallel
        self.cells = []
        self.total_voltage = 0
        self.current = 0
        self.max_current = parallel * max_i
        self.min_current = parallel * min_i
        self.high_cell = 0
        self.low_cell = 0
        self.cell_capacity = capacity  # Cell capacity mAh
        self.module_capacity = capacity * parallel  # Module capacity mAh
        self.total_capacity = series * nom_v * parallel * capacity  # Calculate total battery capacity Whr
        self.internal_resistance = series * (1 / (parallel / avg_z))

        self.create_cell_values(nom_v)
        self.update_total_voltage()
        self.update_min_max()

        print("Battery created")
        print("Calculated values: ")
        print("Cell count: " + str(series * parallel))
        print("Total Capacity: " + str(self.total_capacity) + " Whr")
        print("Internal Resistance: " + str(self.internal_resistance) + " ohms")

    def create_cell_values(self, nom_v):
        i = 0
        while i < self.series:
            i += 1
            n = random.randint(1, 10)
            if n <= 3:
                self.cells.append(round(nom_v - 0.05, 2))
            elif 3 < n <= 7:
                self.cells.append(nom_v)
            elif n > 7:
                self.cells.append(round(nom_v + 0.05, 2))

    def update_total_voltage(self):
        for i in self.cells:
            self.total_voltage += i

    def update_min_max(self):
        self.high_cell = max(self.cells)
        self.low_cell = min(self.cells)

    def update_cell_voltages(self, dv):
        for i in self.cells:
            i -= dv

    def calculate_resistance_drop(self, current=0):
        # Calculates the voltage drop due to the internal resistance at high current
        if current == 0:
            current = self.current
        dv = current * self.internal_resistance
        return dv


class Sun:

    def __init__(self):
        self.irradiance = 1000
        self.status = "Clear"  # TODO add additional weather effects


class Motor:

    def __init__(self, mass, efficiency=0.95):
        self.efficiency = efficiency
        self.mass = mass  # Mass of the car in Kgs
        self.velocity = 0  # Velocity of car in m/s


class DataGenerator:

    def __init__(self, array, battery, sun, motor, sim_time=60):
        self.current_time = 0
        self.time_step = 30  # Simulation time between data points in seconds
        self.sim_time = sim_time  # Length of time to generate simulation data for, in minutes
        self.Array = array  # Array object used in simulation
        self.Battery = battery  # Battery object used in simulation
        self.Sun = sun  # Sun object used in simulation
        self.Motor = motor  # Motor object used in simulation
        self.inst_array_power = self.Array.area * self.Array.efficiency * self.Sun.irradiance
        self.data = {}

        print("Simulator ready")

    def run(self):
        last_save = 0
        while self.current_time < self.sim_time * 60 + 1:  # while the simulation has not run to the specified time
            print("running at time: " + str(self.current_time))
            current_data = {
                "Battery Voltage": self.Battery.total_voltage,
                "Battery Current": self.Battery.current,
                # "Cell Voltages" : self.Battery.cells
                "High Cell": self.Battery.high_cell,
                "Low Cell": self.Battery.low_cell
            }
            self.data[self.current_time] = current_data  # Add data at current time to data log
            if self.current_time - last_save >= 300:  # Save data every 5 simulated minutes
                write_data(self.data)
            self.current_time += self.time_step  # Increment simulation clock

    def calculate_energy(self):
        energy = self.time_step * self.Battery.total_voltage * self.Battery.current
        return energy

    def calculate_voltage_change(self, energy):
        dv = energy / (self.Battery.current * self.time_step)
        return dv

    def accelerate(self, target):
        starting_energy = 0.5 * self.Motor.mass * self.Motor.velocity * self.Motor.velocity
        ending_energy = 0.5 * self.Motor.mass * target * target
        energy_change = ending_energy - starting_energy
        max_power = self.Battery.max_current * self.Battery.total_voltage - (
                    self.Battery.calculate_resistance_drop(self.Battery.max_current)
                    )
        time_required = energy_change / max_power
        print(time_required)
# def write_database(server, database, table, data):
#     print("attempting to connect")
#     connection = pyodbc.connect("Driver={SQL Server};"
#                                 "Server=" + server + ";"
#                                 "Database=" + database + ";"
#                                 "Trusted_Connection=yes;")
#     cursor = connection.cursor()
#     print("Connected")
#     cursor.execute("INSERT INTO " + database + ".dbo." + table +
#                    " (Time, Array_Power, Array_Voltage, Array_Current) VALUES ", str(data))


def write_data(data):
    with open("data_file.json", "w") as write_file:
        json.dump(data, write_file)

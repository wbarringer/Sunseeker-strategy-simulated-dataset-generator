# Tools for generating a simulation dataset that can be used to test and train strategy software

import json
import random
import math


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
            self.efficiency = 0.243

        print("Array created")


class Battery:

    def __init__(self, series, parallel, capacity, max_v=4.2, nom_v=3.6, min_v=2.8, max_i=1, min_i=-1, avg_z=.034):
        self.series = series
        self.parallel = parallel
        self.cells = []
        self.total_voltage = 0
        self.current = 0.001
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
        print("Internal Resistance: " + str(round(self.internal_resistance, 6)) + " ohms")

    def create_cell_values(self, nom_v):
        i = 0
        while i < self.series:
            i += 1
            n = random.randint(1, 10)
            if n <= 3:
                self.cells.append(round(nom_v - 0.01 * random.randint(1, 5), 2))
            elif 3 < n <= 7:
                self.cells.append(nom_v)
            elif n > 7:
                self.cells.append(round(nom_v + 0.01 * random.randint(1, 5), 2))

    def update_total_voltage(self):
        self.total_voltage = 0
        for i in self.cells:
            self.total_voltage += i
        # print(self.total_voltage)

    def update_min_max(self):
        self.high_cell = max(self.cells)
        self.low_cell = min(self.cells)

    def update_cell_voltages(self, dv):
        print(dv)
        for i in self.cells:
            i -= dv
        print(self.cells[0])
        self.update_total_voltage()
        self.update_min_max()

    def calculate_resistance_drop(self, current=0):
        # Calculates the voltage drop due to the internal resistance at high current
        if current == 0:
            current = self.current
        dv = current * self.internal_resistance
        # print("Voltage drop: " + str(dv))
        return dv


class Sun:

    def __init__(self):
        self.irradiance = 1000  # Solar irradiance in W/m^2
        self.status = "Clear"  # TODO add additional weather effects


class Motor:

    def __init__(self, mass, efficiency):
        self.efficiency = efficiency
        self.mass = mass  # Mass of the car in lbs
        self.velocity = 0  # Velocity of car in ft/s
        self.acceleration = 0  # Acceleration of car in ft/s^2
        self.current = 0


class DataGenerator:

    def __init__(self, logging=False, sim_time=60, battery_series=35, battery_parallel=12, battery_capacity=3300,
                 motor_mass=700, motor_efficiency=0.95, current_limit=25):
        self.logging = logging
        self.elapsed_time = 0
        self.time_step = 1  # Simulation time between data points in seconds
        self.sim_time = sim_time  # Length of time to generate simulation data for, in minutes
        self.Array = Array()  # Array object used in simulation
        self.Battery = Battery(battery_series, battery_parallel, battery_capacity)  # Battery object used in simulation
        self.Sun = Sun()  # Sun object used in simulation
        self.Motor = Motor(motor_mass, motor_efficiency)  # Motor object used in simulation
        self.inst_array_power = self.Array.area * self.Array.efficiency * self.Sun.irradiance
        print(self.inst_array_power)
        self.current_limit = current_limit
        self.data = {}
        self.route = {}
        self.route_step = 0
        self.final_step = 0
        self.distance_traveled = 0  # Distance traveled by car in ft
        self.route_distance = 0  # Route length up to the current route step

        print("Simulator ready")

    def run_time_based(self):
        last_save = 0
        while self.elapsed_time < self.sim_time * 60 + 1:  # while the simulation has not run to the specified time
            print("running at time: " + str(self.elapsed_time))
            current_data = {
                "Battery Voltage": self.Battery.total_voltage,
                "Battery Current": self.Battery.current,
                "Cell Voltages": self.Battery.cells,
                "High Cell": self.Battery.high_cell,
                "Low Cell": self.Battery.low_cell
            }
            self.data[self.elapsed_time] = current_data  # Add data at current time to data log
            if self.elapsed_time - last_save >= 300:  # Save data every 5 simulated minutes
                write_data(self.data)
            self.elapsed_time += self.time_step  # Increment simulation clock

    def run_route_based(self, route_file):
        last_save = 0
        with open(route_file) as file_object:
            self.route = json.load(file_object)
        self.final_step = int(max(self.route.keys()))
        while self.route_step <= self.final_step:

            self.update_velocity()
            self.update_position()

            print()
            print(str(self.elapsed_time) + " seconds")
            print("Step " + str(self.route_step))
            print(str(self.distance_traveled) + " feet")
            print("Speed target " + str(self.route[str(self.route_step)]["Speed_Limit"]))
            print("Current speed " + str(self.Motor.velocity / 0.681818))

            if self.distance_traveled - int(self.route[str(self.route_step)]["Distance"]) * 5280 >= self.route_distance:
                print(self.distance_traveled - int(self.route[str(self.route_step)]["Distance"]))
                self.route_distance += int(self.route[str(self.route_step)]["Distance"]) * 5280
                self.route_step += 1
                if self.route_step > self.final_step:
                    break

            if self.Motor.velocity / 0.681818 - int(self.route[str(self.route_step)]["Speed_Limit"]) <= -1:
                # print(self.Motor.velocity / 0.681818)
                # print(self.route[str(self.route_step)]["Speed_Limit"])
                self.accelerate(int(self.route[str(self.route_step)]["Speed_Limit"]))
            elif -1 < self.Motor.velocity / 0.681818 - int(self.route[str(self.route_step)]["Speed_Limit"]) < 1:
                self.hold()
            elif self.Motor.velocity / 0.681818 - int(self.route[str(self.route_step)]["Speed_Limit"]) >= 1:
                self.Motor.acceleration = -0.5  # Placeholder constant deceleration when above speed limit

            self.Battery.update_cell_voltages(
                self.calculate_voltage_change(
                    self.calculate_energy()) / self.Battery.series)
            # print(self.calculate_energy())
            if self.logging is True:
                self.update_log()
                if self.elapsed_time - last_save >= 300:  # Save data every 5 simulated minutes
                    write_data(self.data)
                    last_save = self.elapsed_time
            self.elapsed_time += self.time_step

    def calculate_energy(self):
        energy = self.time_step * self.Battery.total_voltage * self.Battery.current
        return energy

    def calculate_voltage_change(self, energy):
        dv = energy / (self.Battery.current * self.time_step)
        return dv

    def update_position(self):
        dx = self.time_step * self.Motor.velocity + 0.5 * self.Motor.acceleration * (self.time_step ** 2)
        self.distance_traveled += dx

    def update_velocity(self):
        dv = self.time_step * self.Motor.acceleration
        self.Motor.velocity += dv

    def accelerate(self, target, current_limit=25):
        error = (self.Motor.velocity / 0.681818 - target) ** 2
        # current = 0
        if error >= 25:
            print("Significant speed error " + str(error))
            current = current_limit
        elif 25 > error >= 2:
            print("Minor speed error " + str(error))
            current = error * current_limit / 25
        else:
            print("Negligible speed error " + str(error))
            current = 2
        power = current * (self.Battery.total_voltage - self.Battery.calculate_resistance_drop(current))\
                + self.inst_array_power
        print("Power: " + str(power))
        print(current)
        self.Battery.current = current
        self.Battery.update_cell_voltages(self.Battery.calculate_resistance_drop() / self.Battery.series)
        self.Motor.current = power / self.Battery.total_voltage
        self.Motor.acceleration = math.sqrt(
            (power * self.Motor.efficiency) / (2 * self.Motor.mass * self.time_step))
        print("Acceleration: " + str(self.Motor.acceleration))
        print("Motor current: " + str(self.Motor.current))

    def regen(self):
        # TODO complete regen
        print("placeholder")

    def hold(self):
        constant_power = 850  # Power needed for the car to maintain a constant velocity
        current = (constant_power - self.inst_array_power) / self.Battery.total_voltage
        self.Battery.current = current
        self.Battery.update_cell_voltages(self.Battery.calculate_resistance_drop(current) / self.Battery.series)
        self.Motor.acceleration = 0

    def update_log(self):
        current_data = {
            "Battery Voltage": self.Battery.total_voltage,
            "Battery Current": self.Battery.current,
            # "Cell Voltages" : self.Battery.cells,
            "High Cell": self.Battery.high_cell,
            "Low Cell": self.Battery.low_cell,
            "Distance traveled": self.distance_traveled,
            "Velocity": self.Motor.velocity,
            "Acceleration": self.Motor.acceleration
        }
        self.data[self.elapsed_time] = current_data  # Add data at current time to data log


def write_data(data):
    with open("data_file.json", "w") as write_file:
        json.dump(data, write_file)

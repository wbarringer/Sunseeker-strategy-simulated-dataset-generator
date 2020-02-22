# Tools for generating a simulation dataset that can be used to test and train strategy software

# import random
import pyodbc


class TimeGenerator:

    def __init__(self):
        current_time = 0
        time_step = 30  # Simulation time between data points in second

    # def


def write_database(server, database, table, data):
    print("attempting to connect")
    connection = pyodbc.connect("Driver={SQL Server};"
                                "Server=" + server + ";"
                                "Database=" + database + ";"
                                "Trusted_Connection=yes;")
    cursor = connection.cursor()
    print("Connected")
    cursor.execute("INSERT INTO " + database + ".dbo." + table +
                   " (Time, Array_Power, Array_Voltage, Array_Current) VALUES ", str(data))

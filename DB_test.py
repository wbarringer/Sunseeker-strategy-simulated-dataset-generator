# Test program for testing other tools

import GenTools
import pyodbc

server = "CAE-FALL2019-CA\SUNSEEKER_Test"
database = "DataGenerationTestDB"
table = "Array"

if __name__ == '__main__':
    print("This worked, I guess")
    GenTools.write_database(server, database, table, ('12:15:25', '615', '123', '5'))
    # conn = pyodbc.connect("Driver={SQL Server};"
    #                       "Server=CAE-FALL2019-CA\SUNSEEKER_Test;"
    #                       "Database=DataGenerationTestDB;"
    #                       "Trusted_Connection=yes;")
    # cursor = conn.cursor()
    # cursor.execute("""
    #                 INSERT INTO DataGenerationTestDB.dbo.Array (Time, Array_Power, Array_Voltage, Array_Current)
    #
    #                 VALUES
    #                 ('12:15:05', '600', '120', '5'),
    #                 ('12:15:10', '605', '121', '5'),
    #                 ('12:15:15', '610', '122', '5'),
    #                 ('12:15:20', '615', '123', '5')
    #                 """)
    conn.commit()


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


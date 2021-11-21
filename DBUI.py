import pyodbc
import requests

print ('Initiated program')

conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:DB.accdb;')
cursor = conn.cursor()

print ('connection to DB established')


def select():
    #ln =  input('Enter loinc-num ')
    #firstName, lastName = input ('Enter patients\' name').split()
    #date = input('Enter date')
    #cursor.execute('SELECT LOINC\-NUM from medicalRecord where First name=? and Last name=? and Transaction time=?', firstName, lastName, date)
    return

def history():
    return

def update():
    return

def delete():
    return

def exit():
    exit()
    
tasks = {
    1 : select,
    2 : history,
    3 : update,
    4 : delete,
    5 : exit
}


# The program UI

while(True):
    print('Please choose one of the following options (enter the number):\n\
1. SELECT\n2. HISTORY\n3. UPDATE\n4. DELETE\n5. EXIT\n')

    inp = int(input('Task number: '))
    tasks[inp]()
# cursor.execute('select * from medicalRecord')
   
# for row in cursor.fetchall():
#     print (row)
import pyodbc

print ('Initiated program')

conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:DB.accdb;')
cursor = conn.cursor()

print ('connection to DB established')


def select(info):
    return

def history(info):
    return

def update(info):
    return

def delete(info):
    return

def exit():
    exit()
    
tasks = {
    'SELECT' : select,
    'HISTORY' : history,
    'UPDATE' : update,
    'DELETE' : delete,
    'EXIT' : exit
    }


# The program UI
print('name')
while(True):
    inp = input('Query: ').split()
    tasks[inp[0]](inp)
# cursor.execute('select * from medicalRecord')
   
# for row in cursor.fetchall():
#     print (row)
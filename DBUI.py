import pyodbc


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


# The program UI
# print('name')
# while(True):
#     inp = input('Query: ').split()
#     tasks[inp[0]](inp)



##########################################fetch###############################
#lonic = input("lonic: ")
#name = input("name: ")
#component = input("component: ")
#lonic = input("lonic :")
#date = input("date: ")
# hour = date hour splited
# askedIn = input("asking in question in(enter 0 for "now"):")
# check askedIn

# cursor.execute('SELECT * FROM medicalRecord WHERE [First name]=? and [Last name]=? and [LOINC NUM]=?',"Eli","Call","11218-5")
   
# for row in cursor.fetchall():
#         print (row)

########################################fetch history ###########################
# #read data and check about date range values.
# cursor.execute('SELECT * FROM medicalRecord WHERE [First name]=? and [Last name]=? and [LOINC NUM]=? and [Transaction time] between ? and ?'
# ,"Eyal","Rothman","11218-5", "21/5/2018 10:00","22/5/2018 10:00")
   
# for row in cursor.fetchall():
#    # if(row.__contains__("13:11:00")):
#         print (row)


###############################needs to be done at the start ##############################
# add a deleted column at the start of the program if cloumn doesnt exists
try:
    cursor.execute('ALTER TABLE medicalRecord ADD deleted text')
    cursor.commit()
except:
    pass
############################################# insert a new row ##################################
cursor.execute('INSERT INTO medicalRecord ([First name], [Value]) values (?,?)', "100","100")
cursor.commit()












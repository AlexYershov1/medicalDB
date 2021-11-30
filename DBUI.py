from typing import NoReturn
import pyodbc
import re
import csv
import pandas
from datetime import datetime

print('Initiated program')
cases = (True, False, 'special')


def printData(columns, row) -> None:
    print()
    print('result:')
    for column, word in zip(columns, row):
        print(column + ': ' + str(word) + ', ', end=' ')
    print()
    print()
    

def valid_date(s: str) -> bool:
    try:
        mat = re.match(
            '((\d{1,2})[/.-](\d{1,2})[/.-](\d{4})) (0|(\d{1,2}):(\d{1,2}))', s)
        if mat is not None:
            # 1 is full date
            # 2 is day
            # 3 is month
            # 4 is year
            # 5 is time
            # 6 is hour
            # 7 is minute

            if 0 <= int(mat.group(2)) <= 31 and 1 <= int(mat.group(3)) <= 12 and int(mat.group(4)) <= 2022:
                pass
            else:
                return False

            if mat.group(5) == '0':
                return 'special'
            if 0 <= int(mat.group(6)) < 24 and 0 <= int(mat.group(7)) < 60:
                return True
    except ValueError:
        pass
    return False


print('Do you wish to proceed with the existing database or switch to a different one?')

conn = pyodbc.connect(
    r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:DB.accdb;')
cursor = conn.cursor()

print('connection to DB established')

# for row in cursor.columns(table='medicalRecord'):
#         print(row.data_type)

# switching
answer = ''
#while(answer != 's' and answer != 'p' and answer != 'a'):
 #   answer = input('press p to procceed, s to switch, a to add: ')
if answer == 'a':

    file = open('testcsv.xlsx', 'r').read()
    for line in file:
        print(line)
        # Create query over here
        try:
            strSQL = "ALTER TABLE medicalRecord INSERT deleted INTEGER"
            cursor.execute(strSQL)
            conn.commit()
        except:
            pass

    strSQL = "SELECT * INTO medicalRecord FROM [text;HDR=Yes;FMT=Delimited(,);" + \
        "Database=C:].testcsv.csv;"
    cursor.execute(strSQL)
    conn.commit()
# if answer == 's':
#     strSQL = "SELECT * INTO medicalRecord FROM [text;HDR=Yes;FMT=Delimited(,);" + \
#          "Database=C:].newDB.csv;"
#     cursor.execute(strSQL)
#     conn.commit()


class lonicDB:
    def __init__(self) -> None:
        global cursor
        try:
            cursor.execute('ALTER TABLE medicalRecord ADD deleted datetime')
            cursor.commit()
        except:
            pass
        try:
            cursor.execute(
                'ALTER TABLE medicalRecord ADD LONG_COMMON_NAME text')
            cursor.commit()

            cursor.execute('SELECT [LOINC-NUM] from medicalRecord')
            loincs = cursor.fetchall()
            loincSet = set()
            [loincSet.add(x[0]) for x in loincs]

            for loinc in loincSet:
                cursor.execute(
                    'SELECT * from LoincTable WHERE [LOINC_NUM]=?', loinc)
                lcn = cursor.fetchone()
                if lcn:
                    cursor.execute(
                        'UPDATE medicalRecord SET [LONG_COMMON_NAME]=? WHERE [LOINC-NUM]=?', lcn[2], loinc)
            cursor.commit()
        except:
            pass

    def delete(self):
        global cursor
        try:
            cursor.execute('ALTER TABLE medicalRecord DELETE deleted')
            cursor.commit()
        except:
            pass
        try:
            cursor.execute('ALTER TABLE medicalRecord DELETE LONG_COMMON_NAME')
            cursor.commit()
        except:
            pass
    
    def select(self):
        pass


def select():
    loinc = input("enter lonic-num or component: ")
    first_name = input("enter first name: ")
    last_name = input("enter last name: ")
    date = input("date: ")
    viewPointDate = input("searching at(enter 0 for now): ")
    date2 =""
    datevalid = valid_date(date)
    if(datevalid == True):
        if(datevalid == 'special'):
            date = date[:-1]
            date2 = date
            date += "00:00"
            date2 += "23:59"
        else:
            date2 = date
    else:
        print("invalid date")
        return

    if (viewPointDate == '0'):
        viewPointDate = datetime.now().strftime("%d/%m/%Y %H:%M")
    # date2
    # if date has no hour  - date hour = 0:00 and date2 hour = 23:59
    # if date has hour date2 hour = date hour
    # first_name, last_name, loinc, date, viewPointDate = 'Eyal', 'Rothman', '11218-5', '18-5-2018 11:00', datetime.now().strftime("%d/%m/%Y %H:%M")
    # date2 = date
    cursor.execute('SELECT * FROM medicalRecord WHERE [First name]=? and [Last name]=? and [LOINC-NUM]=?\
        and [Valid start time] between ? and ? and [Transaction time] <= ? order by [Valid start time] desc',
                   first_name, last_name, loinc, date, date2, viewPointDate)

    rows = cursor.fetchall()
    if (len(rows) == 0):
        print("could not find such case that meets the criteria specified")
        return

    # get fields names and index of te deleted field
    columns = [column[0] for column in cursor.description]  
    index = [column[0] for column in cursor.description].index('deleted')

    for row in rows:
        if(row[index] == None or row[index] < datetime.strptime(viewPointDate, "%d/%m/%Y %H:%M")):
            printData(columns, row)
            return
            
    print("could not find such case that meets the criteria specified")
    return


def history():
    loinc = input("enter loinc-num or component : ")
    first_name = input("enter first name: ")
    last_name = input("enter last name: ")
    dateDis = input(
        "enter the valid date time and hour to display from, 0 hour for all day: ")
    fromd = input(
        "enter : transaction time range, from (0 for 1/1/1900 till now):")
    if (fromd != '0'):
        tod = input("to transaction time date and hour: ")
    else:
        fromd = "1/1/1900 0:00"
        tod = datetime.now().strftime("%d/%m/%Y %H:%M")
    # dateDis2 = ????
    # ask here if datedis contains hour , if not - set hour to 0:00 , anyway create a second datedis2 - set hour to 23:59 if no hour at
    # datedis , if there is so datedis2 = datedis

    # check if all date inputs are valid inputs

    cursor.execute('SELECT * FROM medicalRecord WHERE [First name]=? and [Last name]=?\
        and ([LOINC-NUM]=? or [LOINC-NUM]=?) and [Valid start time] between ? and ? and [Transaction time] between ? and ?',
         first_name, last_name, loinc, loinc, dateDis, "18/5/2018 19:00", fromd, tod)
    return


def update():
    date = input("enter date of test enter 0 for now: ")
    loinc = input("enter loinc num or component name: ")
    first_name = input("enter first name: ")
    last_name = input("enter last name: ")
    validdate = input("enter valid time: ")
    value = input("new value is: ")
    if date == '0':
        date = datetime.now().strftime("%d/%m/%Y %H:%M")
    elif (valid_date(date) != True):
        print("invalid date")

    #coalesce()

    cursor.execute('SELECT * FROM medicalRecord WHERE ([LOINC-NUM]=? or [LOINC-NUM]=?)\
        and [First name]=? and [Last name]=? and [Valid start time]=? order by [Transaction time] desc',
                   loinc, loinc, first_name, last_name, validdate)

    row = cursor.fetchone()
    if(row):
        cursor.execute('INSERT INTO medicalRecord ([First name], [Last name], [LOINC-NUM], [Value], [Unit], [Valid start time], [Transaction time])\
        values (?,?,?,?,?,?,?)', first_name, last_name, loinc, value, row[5], date, datetime.now().strftime("%d/%m/%Y %H:%M"))
        cursor.commit()
    else:
        print("Could not Find such test to update or one of the arguments is invalid \n")
    return


def delete():
    deleted = input("deleted at:(enter 0 for now) ")
    loinc = input("enter loinc-num or component name: ")
    first_name = input("enter  ")
    last_name = input("deleted at:(enter 0 for now) ")
    valid = input("enter valid start time, enter 0 at hour for the latest update that day: ")
    valid2 = ""

    if(deleted == '0'):
        deleted = datetime.now().strftime("%d/%m/%Y %H:%M")
    elif (valid_date(deleted) != True):
        print("invalid date")
        return
    validDate = valid_date(valid)
    if(validDate == True):
        if(validDate == 'special'):
            valid = valid[:-1]
            valid2 = valid
            valid += "00:00"
            valid2 += "23:59"
        else:
            valid2 = valid
    else:
        print("invalid date")

    cursor.execute('SELECT * FROM medicalRecord WHERE ([LOINC-NUM]=? or [LOINC-NUM]=?) and [First name]=?\
        and [Last name]=? and [deleted]=? and [Valid start time] between ? and ? order by [Valid start time] desc',
                   loinc, loinc, first_name, last_name, None, valid, valid2)

    row = cursor.fetchone()
    if(row):
        id = row[0]
        cursor.execute('UPDATE medicallRecord SET [deleted]=? WHERE [ID]=?', deleted,id)
        # cursor.execute('UPDATE medicallRecord SET [deleted]=? WHERE ([LOINC-NUM]=? or [LOINC-NUM]=?) and [First name]=?\
        #     and [Last name]=? and [Valid start time] between ? and ? ',
        #                deleted, loinc, loinc, first_name, last_name, valid, valid2)
    else:
        print("could not find such case that meets the criteria specified")

    return


tasks = {
    1: select,
    2: history,
    3: update,
    4: delete,
    #5: ChangeTable
}


# The program UI
db = lonicDB()

inp = ''
while(True):
    print('Please choose one of the following options (enter the number):\n\
1. SELECT\n2. HISTORY\n3. UPDATE\n4. DELETE\n5. Change Table\n6. EXIT\n')

    try:
        inp = int(input('Task number: '))
    except ValueError:
        continue

    if inp == 6:
        break
    elif 0 < inp < 6:
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
# cursor.execute('SELECT * FROM medicalRecord WHERE [First name]=? and [Last name]=? '
# 'and ([LOINC NUM]=? or [LOINC NUM]=?) and [Valid start time] between ? and ? and [Transaction time] between ? and ?'
#  ,"Eyal","Rothman","11218-5","common name","17/5/2018 17:00", "18/5/2018 19:00", "20/5/2018 10:00","28/5/2018 10:00")
# =======
# cursor.execute('select * from medicalRecord')

# for row in cursor.fetchall():
#    # if(row.__contains__("13:11:00")):
#         print (row)


###############################needs to be done at the start ##############################
# add a deleted column at the start of the program if cloumn doesnt exists
"""
try:
    cursor.execute('ALTER TABLE medicalRecord ADD deleted text')
    cursor.commit()
except:
    pass
try:
    cursor.execute('ALTER TABLE medicalRecord ADD LONG_COMMON_NAME text')
    cursor.commit()
except:
    pass

############################################# insert a new row ##################################
cursor.execute('INSERT INTO medicalRecord ([First name], [Value]) values (?,?)', "100","100")
cursor.commit()
"""

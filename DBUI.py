import pyodbc
import re
from datetime import datetime

print('Initiated program')

def printData(columns, row) -> None:
    print()
    print('result:')
    for column, word in zip(columns, row):
        print(column + ': ' + str(word) + ', ', end=' ')
    print()
    

def valid_date(s: str):
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


conn = pyodbc.connect(
    r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:DB.accdb;')
cursor = conn.cursor()

print('connection to DB established')


class lonicDB:
    def __init__(self, tableName) -> None:
        self.tableName = tableName

        global cursor
        try:
            cursor.execute(f'ALTER TABLE {tableName} ADD deleted datetime')
            cursor.commit()
        except:
            pass
        try:
            cursor.execute(
                f'ALTER TABLE {tableName} ADD LONG_COMMON_NAME text')
            cursor.commit()

            cursor.execute(f'SELECT [LOINC-NUM] from {tableName}')
            loincs = cursor.fetchall()
            loincSet = set()
            [loincSet.add(x[0]) for x in loincs]

            for loinc in loincSet:
                cursor.execute(
                    'SELECT * from LoincTable WHERE [LOINC_NUM]=?', loinc)
                lcn = cursor.fetchone()
                if lcn:
                    cursor.execute(
                        f'UPDATE {tableName} SET [LONG_COMMON_NAME]=? WHERE [LOINC-NUM]=?', lcn[2], loinc)
            cursor.commit()
        except:
            pass
        
    @property
    def name(self):
        return self.tableName
    @name.setter
    def name(self, newData):
        self.tableName = newData

    def select(self):
        loinc = input("enter lonic-num or component: ")
        first_name = input("enter first name: ")
        last_name = input("enter last name: ")
        date = input("date: ")
        viewPointDate = input("searching at(enter 0 for now): ")
        date2 =""
        datevalid = valid_date(date)
        if(datevalid == 'special'):
            date = date[:-1]
            date2 = date
            date += "00:00"
            date2 += "23:59"
        elif(datevalid == True):
            date2 = date
        else:
            print("invalid date")
            return

        if (viewPointDate == '0'):
            viewPointDate = datetime.now().strftime("%d/%m/%Y %H:%M")
        elif(viewPointDate != True):
            print("invalid searching at date")
            return
    
        #first_name, last_name, loinc, date, viewPointDate = 'Eyal', 'Rothman', '11218-5', '18-5-2018 11:00', datetime.now().strftime("%d/%m/%Y %H:%M")
        #date2 = date
        cursor.execute(f'SELECT * FROM {self.name} WHERE [First name]=? and [Last name]=? and [LOINC-NUM]=?\
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
            if(row[index] == None or row[index] > datetime.strptime(viewPointDate, "%d/%m/%Y %H:%M")): #no way that this throw excp?
                printData(columns, row)
                return
                
        print("could not find such case that meets the criteria specified")
        return


    def history(self):
        loinc = input("enter loinc-num or component : ")
        first_name = input("enter first name: ")
        last_name = input("enter last name: ")
        dateDis = input("enter the valid date time and hour to display from, 0 hour for all day: ")
        dateDis2 = ""
        fromd = input("enter transaction time range, from (0 for 1/1/1900 till now, 0 at hour only = from 00:00):")
        if (fromd != '0'):
            tod = input("to transaction time date and hour (enter 0 at hour for 23:59): ")
        else:
            fromd = "1/1/1900 0:00"
            tod = datetime.now().strftime("%d/%m/%Y %H:%M")
        if(valid_date(fromd) == False or valid_date(tod) == False):
            print("invalid dates range")
            return
        elif(valid_date(fromd) == 'special'):
            if(valid_date(tod) == 'special'):
                tod = tod[:-1] + "23:59" # not sure thats what she wants here, do i need to print an error? 
            fromd = fromd[:-1] + "00:00"

        validDate = valid_date(dateDis)
        if(validDate == 'special'):
            dateDis = dateDis[:-1]
            dateDis2 = dateDis
            dateDis += "00:00"
            dateDis2 += "23:59"
        elif(validDate == True):
            dateDis2 = dateDis
        else:
            print("invalid date")

        cursor.execute(f'SELECT * FROM {self.name} WHERE [First name]=? and [Last name]=?\
            and ([LOINC-NUM]=? or [LOINC-NUM]=?) and [Valid start time] between ? and ? and [Transaction time] between ? and ?',
            first_name, last_name, loinc, loinc, dateDis, dateDis2, fromd, tod)

        rows = cursor.fetchall()
        if (len(rows) == 0):
            print("could not find such case that meets the criteria specified")
            return
        columns = [column[0] for column in cursor.description]  
        index = [column[0] for column in cursor.description].index('deleted')

        for row in rows:
            if(row[index] == None or row[index] > datetime.strptime(tod, "%d/%m/%Y %H:%M") or row[index] < datetime.strptime(fromd, "%d/%m/%Y %H:%M")): 
                printData(columns, row)
                return
        return


    def update(self):
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
            return
        if (valid_date(validdate) != True):
            print("invalid valid date time")
            return


        cursor.execute(f'SELECT * FROM {self.name} WHERE ([LOINC-NUM]=? or [LOINC-NUM]=?)\
            and [First name]=? and [Last name]=? and [Valid start time]=? order by [Transaction time] desc',
                    loinc, loinc, first_name, last_name, validdate)

        row = cursor.fetchone()
        ## need to change here from row[5] to what alex did with row[9] ######################################
        if(row):
            cursor.execute(f'INSERT INTO {self.name} ([First name], [Last name], [LOINC-NUM], [Value], [Unit], [Valid start time], [Transaction time])\
            values (?,?,?,?,?,?,?)', first_name, last_name, loinc, value, row[5], date, datetime.now().strftime("%d/%m/%Y %H:%M"))
            cursor.commit()
        else:
            print("Could not Find such test to update or one of the arguments is incorrect \n")
        return


    def delete(self):
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
        if(validDate == 'special'):
            valid = valid[:-1]
            valid2 = valid
            valid += "00:00"
            valid2 += "23:59"
        elif(validDate == True):
            valid2 = valid
        else:
            print("invalid date")

        cursor.execute(f'SELECT * FROM {self.name} WHERE ([LOINC-NUM]=? or [LOINC-NUM]=?) and [First name]=?\
            and [Last name]=? and [deleted]=? and [Valid start time] between ? and ? order by [Valid start time] desc',
                    loinc, loinc, first_name, last_name, None, valid, valid2)

        row = cursor.fetchone()
        if(row):
            id = row[0]
            cursor.execute(f'UPDATE {self.name} SET [deleted]=? WHERE [ID]=?', deleted,id)
            # cursor.execute('UPDATE medicallRecord SET [deleted]=? WHERE ([LOINC-NUM]=? or [LOINC-NUM]=?) and [First name]=?\
            #     and [Last name]=? and [Valid start time] between ? and ? ',
            #                deleted, loinc, loinc, first_name, last_name, valid, valid2)
        else:
            print("could not find such case that meets the criteria specified")

        return


def select(db: lonicDB):
    db.select()

def history(db: lonicDB):
    db.history()

def update(db: lonicDB):
    db.update()

def delete(db: lonicDB):
    db.delete()

def changeTable(dbPuppet: lonicDB):
    global db
    answer =''
    while answer != 'a' and answer != 's' and answer != 'c':
        answer = input('Choose operation <a to add, s to switch, c to cancel>: ')
    
    if answer == 'a':
        newTable = ''
        while newTable != 'c':
            newTable = input('Enter new table name or c to cancel: ')
            try:
                assert cursor.execute(f'SELECT * FROM {newTable}')
                lonicDB(newTable)
                # cursor.execute(f'SELECT [ID], [First name], [Last name], [LOINC-NUM], [Value], [Unit], [Valid start time],[Transaction time],\
                #  [deleted], [LONG_COMMON_NAME] FROM {db.name}\
                #   UNION ALL SELECT [ID], [First name], [Last name], [LOINC-NUM], [Value], [Unit], [Valid start time], [Transaction time], [deleted], [LONG_COMMON_NAME] FROM {newTable}')
                cursor.execute(f'SELECT * FROM {newTable}')
                rows = cursor.fetchall()
                for row in rows:
                    cursor.execute(f'INSERT INTO {db.name} ([First name], [Last name], [LOINC-NUM], [Value], [Unit], [Valid start time], [Transaction time], [deleted], [LONG_COMMON_NAME]) values (?,?,?,?,?,?,?,?,?)', row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
                cursor.commit

                return
            except:
                pass
    elif answer == 's':
        newTable = ''
        while newTable != 'c':
            newTable = input('Enter new table name or c to cancel: ')
            try:
                assert cursor.execute(f'SELECT * FROM {newTable}')
                db = lonicDB(newTable)
                print('switch complete')
                return
            except :
                pass
    else:
        return     

tasks = {
    1: select,
    2: history,
    3: update,
    4: delete,
    5: changeTable
}


# The program UI
db = lonicDB('medicalRecord')

inp = ''
while(True):
    print()
    print('Please choose one of the following options (enter the number):\n\
1. SELECT\n2. HISTORY\n3. UPDATE\n4. DELETE\n5. Change Table\n6. EXIT\n')

    try:
        inp = int(input('Task number: '))
    except ValueError:
        continue

    if inp == 6:
        break
    elif 0 < inp < 6:
        tasks[inp](db)


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

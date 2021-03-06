import os
import mysql.connector
import zipfile

rootdir = "/root/Resources/"

def main():
    mydb = mysql.connector.connect(
        host="localhost",
        user="foo",
        passwd="bar",
        db = "GEE_DB"
        )
    meta(mydb)
    zipFiles(mydb)
    processPdfLocation(mydb)

def meta(mydb):
        print("Database connection is successful")
        print("Now starting processing of directories!")
        for subdir, dirs, files in os.walk(rootdir):
                for file in files:
                    file_string = str(file)
                    if(str(file) == "Meta.txt"):
                        processMetaFile(os.path.join(subdir, file), mydb)
                        print("yes")
                    elif (file_string[-3:] == "pdf"):
                        pdfLocation(os.path.join(subdir, file), mydb, subdir, file)

def processPdfLocation(mydb):
    for subdir, dirs, files in os.walk(rootdir):
                for file in files:
                    file_string = str(file)
                    if (file_string[-3:] == "pdf"):
                        pdfLocation(os.path.join(subdir, file), mydb, subdir, file)

def pdfLocation(file_contents_in, mydb, subdir, file):
    mycursor = mydb.cursor()
    sql_check_for_existing = "SELECT fileid FROM OER where filelocation = \"" + subdir + "\""
    mycursor.execute(sql_check_for_existing)
    myresult = mycursor.fetchall()
    if len(myresult) > 0:
        for row in myresult:
            insert_sql = "UPDATE OER SET pdflocation = \"" + os.path.join(subdir, file) + "\" WHERE fileid = " + str(row[0])
        mycursor.execute(insert_sql)
        mydb.commit()
    
def zipFiles(mydb):
    for folder in os.listdir(rootdir):
        print("FOLDER EXT", folder[-3:])
        folder_string = str(folder)
        if folder_string[-3:] == "zip" or folder_string[-3:] == "rar":
            print("Zip found, now skipping")
        else:
            print("Unzipped folder found, now zipping: ", folder)
            zipf = zipfile.ZipFile('{0}.zip'.format(os.path.join(rootdir, folder)), 'w', zipfile.ZIP_DEFLATED)
            for root, dirs, files in os.walk(os.path.join(rootdir, folder)):
                for filename in files:
                    zipf.write(os.path.abspath(os.path.join(root, filename)), arcname=filename)
            zipf.close()


def processZipFile(subdir, list_of_files):
    print("This is the sub directory:",  subdir)
    zipObj = ZipFile(subdir + ".zip", 'w')
    for file in list_of_files:
        zipObj.write(file)
    zipObj.close()
    
def processMetaFile(file, mydb):
        with open(file) as f:
                file_contents = f.read()
                processFileContents(file_contents, mydb)

def processFileContents(file_contents_in, mydb):
        userid = 0
        insert_statement = ''
        file_location = ''
        description = ''
        name = ''
        subject = ''
        media_format = ''
        license =  ''
        date_added = ''
        grade = ''
        tags = ''
        author = ''
        fileid = 0
        file_contents_list = file_contents_in.split(':')
        counter = 0
        for s in file_contents_list:
            s = s.strip()
            #print("{",s,"}")
            if s == "Details":
                description = file_contents_list[counter + 1]
            if s == "License":
                license = file_contents_list[counter + 1]
            if s == "Media Format":
                media_format = file_contents_list[counter + 1]
            if s == "Tags":
                tags = file_contents_list[counter + 1]
            if s == "Grades":
                grade = file_contents_list[counter + 1]
            if s == "Author":
                author = file_contents_list[counter + 1]
                #print("This is author:", author)
            if s == "Date Added":
                date_added = file_contents_list[counter + 1]
            if s == "Subject":
                subject = file_contents_list[counter + 1]
            if s == "File Location":
                file_location = file_contents_list[counter + 1]
            counter = counter + 1
       # insert_statement = "INSERT INTO OER (userid, author, filelocation, description, name, subject, mediaformat, license, dateadded, grade, upvotes) VALUES (0,{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10});".format(author, file_location,description,name,subject,media_format, license,date_added,grade,0,tags,"none")
        mycursor = mydb.cursor()
        sql_check_for_existing = "SELECT filelocation FROM OER where filelocation = \"" + file_location + "\""
        mycursor.execute(sql_check_for_existing)
        myresult = mycursor.fetchall()
        insert_sql = "INSERT INTO OER (userid, author, filelocation, description, name, subject, mediaformat, license, dateadded, grade, upvotes, tags, remix) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        insert_val = (0, author, file_location,description,name,subject,media_format, license,date_added,grade,0,tags,"none")
        if len(myresult) == 0:
            mycursor.execute(insert_sql, insert_val)
            mydb.commit()


if __name__ == '__main__':
    main()



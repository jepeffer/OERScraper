
import os
import mysql.connector

rootdir = "/root/Resources/"

def main():
        mydb = mysql.connector.connect(
        host="localhost",
        user="foo",
        passwd="bar",
        db = "GEE_DB"
        )
        print("Database connection is successful")
        print("Now starting processing of directories!")
        for subdir, dirs, files in os.walk(rootdir):
                for file in files:
                        if(str(file) == "Meta.txt"):
                            processMetaFile(os.path.join(subdir, file), mydb)

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
            counter = counter + 1
       # insert_statement = "INSERT INTO OER (userid, author, filelocation, description, name, subject, mediaformat, license, dateadded, grade, upvotes) VALUES (0,{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10});".format(author, file_location,description,name,subject,media_format, license,date_added,grade,0,tags,"none")
        sql = "INSERT INTO OER (userid, author, filelocation, description, name, subject, mediaformat, license, dateadded, grade, upvotes, tags, remix) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (0, author, file_location,description,name,subject,media_format, license,date_added,grade,0,tags,"none")
        #print(sql, val)
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        mydb.commit()


if __name__ == '__main__':
    main()


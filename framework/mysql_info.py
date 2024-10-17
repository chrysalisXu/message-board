"""
This file tells username,password and database of local mysql database.
I assume the user have ALL PRIVILEGES in given database.
whenever this program runs in new machine, please modify these vars.
since you may not have a user named xujing who have all privileges in
mysql database. 
"""


# database info
database_info = {
    'user': 'xujing',
    'host' : 'localhost',
    'password' :  'xujing_pass',
    'database' :  'MessageBoard'
}

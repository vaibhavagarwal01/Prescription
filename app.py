import calendar

from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import mysql.connector
import configparser
from datetime import date

# It is used to get all the configurations from the 'config.txt' file
configParser = configparser.RawConfigParser()
configFilePath = r'config.txt'
configParser.read(configFilePath)

app = Flask(__name__)  # is used to create an instance of the Flask class.
app.secret_key = configParser.get('My-Section', 'flask_secret_key')

mydb = mysql.connector.connect(host=configParser.get('My-Section', 'db_host'),
                               user=configParser.get('My-Section', 'db_user'),
                               password=configParser.get('My-Section', 'db_password'),
                               database=configParser.get('My-Section', 'db_database'))

print(mydb)  # used to check whether the database is connected or not
mycursor = mydb.cursor()  # is used to create a cursor object for interacting with a database


@app.route('/')
def healthCheck():
    return 'Backend is working!'


@app.route('/api/v1/create', methods=["POST"])
def createPrescription():
    input_json = request.get_json(force=True)
    for object in input_json:
        print(object)
        prescriptions_date = date.today()
        print(prescriptions_date)
        sql = "INSERT INTO prescriptions(PatientId, Description, Dosage, Frequency, Duration, Reason, DateOfIssue) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (object['patientId'], object['description'], object['dosage'], object['frequency'],
               object['duration'], object['reason'], prescriptions_date)
        mycursor.execute(sql, val)
        mydb.commit()
    dictToReturn = {"success": True,
                    # "id": mycursor.lastrowid
                    }
    # returning the data in json format
    return jsonify(dictToReturn)

@app.route('/create_prescription/<patient_id>', methods=["GET"])
def createPrescriptionGet(patient_id):
    print(patient_id)
    return render_template('create_prescription.html')



@app.route('/api/v1/getPatients', methods=["GET"])
def getPatients():
    mycursor.execute("SELECT * FROM patients")
    myresult = mycursor.fetchall()  # myresult is list of tuples
    print(myresult)
    all_patients = []
    for x in myresult:
        print(x)
        dict = {
            "patient_id": x[0],
            "patient_name": x[1]
        }
        all_patients.append(dict)
    print(all_patients)
    response = {
        'success': True,
        'data': all_patients
    }
    # return jsonify(response)
    headers = ['Patient Id', 'Patient Name']
    return render_template('list_patients.html', headers=headers, tableData=all_patients)


@app.route('/api/v1/getPrescriptions/<patient_id>', methods=["GET"])
def getPrescriptions(patient_id):
    args = request.args
    print(args)
    sql = "SELECT Description, Dosage, Frequency, Duration, Reason, DateOfIssue from prescriptions where patientid = %s"
    # val = (args.get('patientid'),)
    val = (patient_id, )
    print(type(val))
    print(val)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    all_prescriptions = []
    for object in myresult:
        print(object)
        print(type(object[5]))
        print(object[5])
        date_str = object[5].day
        month_num = object[5].month
        month_name_str = calendar.month_abbr[month_num]
        date = f'{date_str} {month_name_str}'
        dict = {'description': object[0],
                'dosage': object[1],
                'frequency': object[2],
                'duration': object[3],
                'reason': object[4],
                'dateOfIssue': date
                }
        all_prescriptions.append(dict)
    print(all_prescriptions)
    response = {'success': True,
                'data': all_prescriptions
                }
    # return jsonify(response)
    headers = ['Description', 'Dosage', 'Frequency', 'Duration', 'Reason', 'Date of Issue']
    return render_template('get_prescriptions.html', headers=headers, tableData=all_prescriptions, patientId=patient_id)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5009)

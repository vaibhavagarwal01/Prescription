from flask import Flask, render_template, request, redirect
import mysql.connector
import configparser
from datetime import date
import calendar

configParser = configparser.RawConfigParser()
configFilePath = r'config.txt'
configParser.read(configFilePath)

app = Flask(__name__)
app.secret_key = configParser.get('My-Section', 'flask_secret_key')

mydb = mysql.connector.connect(host=configParser.get('My-Section', 'db_host'),
                               user=configParser.get('My-Section', 'db_user'),
                               password=configParser.get('My-Section', 'db_password'),
                               database=configParser.get('My-Section', 'db_database'))
mycursor = mydb.cursor()


@app.route('/')
def healthCheck():
    return 'Backend is working!'


@app.route('/api/v1/create/<patient_id>', methods=["POST"])
def createPrescription(patient_id):
    data = request.form.to_dict(flat=False)
    print(data)
    for i in range(len(data['descriptions[]'])):
        prescriptions_date = date.today()
        sql = "INSERT INTO prescriptions(PatientId, Description, Dosage, Frequency, Duration, Reason, DateOfIssue) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (patient_id, data['descriptions[]'][i], data['dosage[]'][i], data['frequency[]'][i],
               data['duration[]'][i], data['reason[]'][i], prescriptions_date)
        mycursor.execute(sql, val)
        mydb.commit()
    return redirect(f"/getPrescriptions/{patient_id}")


@app.route('/create_prescription/<patient_id>', methods=["GET"])
def createPrescriptionGet(patient_id):
    print(patient_id)
    return render_template('create_prescription.html', patientId=patient_id)


@app.route('/getPatients', methods=["GET"])
def getPatients():
    mycursor.execute("SELECT * FROM patients")
    result = mycursor.fetchall()
    all_patients = []
    for x in result:
        print(x)
        patient = {
            "patient_id": x[0],
            "patient_name": x[1]
        }
        all_patients.append(patient)
    headers = ['Patient Id', 'Patient Name']
    return render_template('list_patients.html', headers=headers, tableData=all_patients)


@app.route('/getPrescriptions/<patient_id>', methods=["GET"])
def getPrescriptions(patient_id):
    args = request.args
    print(args)
    sql = "SELECT Description, Dosage, Frequency, Duration, Reason, DateOfIssue from prescriptions " \
          "where PatientId = %s"
    val = (patient_id,)
    mycursor.execute(sql, val)
    result = mycursor.fetchall()
    all_prescriptions = []
    for object in result:
        date_str = object[5].day
        month_num = object[5].month
        month_name_str = calendar.month_abbr[month_num]
        date_of_issue = f'{date_str} {month_name_str}'
        prescription = {'description': object[0],
                        'dosage': object[1],
                        'frequency': object[2],
                        'duration': object[3],
                        'reason': object[4],
                        'dateOfIssue': date_of_issue}
        all_prescriptions.append(prescription)
    headers = ['Description', 'Dosage', 'Frequency', 'Duration(days)', 'Reason', 'Date of Issue']
    return render_template('get_prescriptions.html', headers=headers, tableData=all_prescriptions, patientId=patient_id)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5009)

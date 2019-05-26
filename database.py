import cx_Oracle

connection = cx_Oracle.connect("CS221", "CS221", "localhost/SEBI.168.86.68")

cursor = connection.cursor()


def insertCompany(company_number, profile, officers, persons_with_significant_control):

    # statement = 'insert into company_profile(company_number, profile, officers, persons_with_significant_control) values (:2, :3, :4, :5)'
    statement = 'MERGE INTO company USING dual ON ( company_number=:2 ) \
                WHEN MATCHED THEN UPDATE SET profile=:3 , officers=:4, persons_with_significant_control=:5 \
                WHEN NOT MATCHED THEN INSERT (company_number, profile, officers, persons_with_significant_control)  \
                VALUES (:2, :3, :4, :5)'
    cursor.execute(statement, (company_number, profile, officers, persons_with_significant_control))
    connection.commit()


def insertOfficer(officer_id, appointments):
    # statement = 'insert into officer(officer_id, appointments) values (:2, :3)'
    statement = 'MERGE INTO officer USING dual ON ( officer_id = :2 ) \
                    WHEN MATCHED THEN UPDATE SET appointments =:3  \
                    WHEN NOT MATCHED THEN INSERT (officer_id, appointments)  \
                    VALUES (:2, :3)'
    cursor.execute(statement, (officer_id, appointments))
    connection.commit()

def updateCompanyPSC(company_number, persons_with_significant_control):
    statement = 'UPDATE company SET persons_with_significant_control = :v WHERE company_number = :k'
    cursor.execute(statement, {'k': company_number, 'v': persons_with_significant_control})
    connection.commit()

def insertPSC(psc_id, psc_data, label):

    statement = 'MERGE INTO person_with_significant_control USING dual ON ( psc_id=:2 ) \
                WHEN MATCHED THEN UPDATE SET psc_data=:3, label=:4  \
                WHEN NOT MATCHED THEN INSERT (psc_id, psc_data, label)  \
                VALUES (:2, :3, :4)'
    cursor.execute(statement, (psc_id, psc_data, label))
    connection.commit()





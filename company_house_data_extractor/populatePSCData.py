from config import *
import cx_Oracle

import json
from jsonpath_ng import jsonpath, parse

log = logging.getLogger('populatePSCData')

connection = cx_Oracle.connect("CS221", "CS221", "localhost/SEBI.168.86.68")

cursor = connection.cursor()


def insertPSC(psc_id, psc_data, label):

    statement = 'MERGE INTO person_with_significant_control USING dual ON ( psc_id=:2 ) \
                WHEN MATCHED THEN UPDATE SET psc_data=:3, label=:4  \
                WHEN NOT MATCHED THEN INSERT (psc_id, psc_data, label)  \
                VALUES (:2, :3, :4)'
    cursor.execute(statement, (psc_id, psc_data, label))
    connection.commit()


def populatePSCData():

    statement = 'select c.label, c.persons_with_significant_control from company c where c.persons_with_significant_control.items is not null'
    cursor.execute(statement)

    results = []

    for result in cursor:
        results.append((result[0], result[1]))

    for result in results:
        label = result[0]
        psc_list_str = result[1]

        psc_list = [psc.value for psc in parse('$.items[*]').find(json.loads(psc_list_str))]
        for psc in psc_list:
            psc_id = parse('$.links.self').find(psc)[0].value.split('/')[-1]

            log.debug('Inserting {}, {}, {} into person_with_significant_control'.format(psc_id, psc, label))
            insertPSC(psc_id, json.dumps(psc), label)

populatePSCData()

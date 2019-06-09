import pandas as pd

from config import *
from data.database import *
import xbrl_parser.parser as xp


import multiprocessing
import xbrl_parser.xbrl_extractor_sample

import timeout_decorator

def initProcess(share):
  xbrl_parser.xbrl_extractor_sample.debt_equity_data = share

log = logging.getLogger('xbrl.py')


def timeout(func, args=(), kwargs={}, timeout_duration=1, default=None):
    import threading
    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None

        def run(self):
            try:
                self.result = func(*args, **kwargs)
            except:
                self.result = default

    it = InterruptableThread()
    it.start()
    it.join(timeout_duration)
    if it.isAlive():
        return default
    else:
        return it.result

def extract_from_xbrl():

    df = pd.read_csv('../data/companies_with_accounts.csv', header=None, dtype=str)

    manager = multiprocessing.Manager()
    debt_equity_data = manager.list()

    list = df.values.copy()
    # list = [['06499726']]
    transactionPool = multiprocessing.Pool(PROCESS_POOL_SIZE, initializer=initProcess, initargs=(debt_equity_data,))
    transactionPool.map(processCompany, list)
    transactionPool.close()
    transactionPool.join()

    results = [data for data in debt_equity_data]
    df = pd.DataFrame(results)
    df.to_csv('../data/company_debt_equity_data.csv', header=['company_number', 'debt', 'equity'], index=False)


def processAccountData(account_data):
    return xp.process_account_data(str(account_data))

def processCompany(input_data):

    company_number = input_data[0]

    try:
        account_data = get_latest_account_for_company(company_number)

        # doc = xp.process_account_data(str(account_data))
        doc = timeout(processAccountData, args=(str(account_data),), timeout_duration=300)
        if doc == None:
            xbrl_parser.xbrl_extractor_sample.debt_equity_data.append(
                [company_number, 0., 0.])

            log.debug(
                'Company - {} timed out'.format(company_number))
            return

        # the shareholder funds/equity
        equity = xp.summarise_by_priority(doc, ["shareholderfunds",
                                                "equity",
                                                "capitalandreserves"], True)
        equity = equity['primary_assets']
        # calculate total debt
        debt = xp.summarise_by_priority(doc, ["totalcreditors", "creditors"], True)
        if debt != None and debt['primary_assets'] == 0.0:
            debt = xp.summarise_by_sum(doc, ["creditorsdueafteroneyear",
                                             "creditorsdueafteroneyearotherthanconvertibledebt",
                                             "creditorsduewithinoneyear",
                                             "creditorsduewithinoneyearotherthanconvertibledebt",
                                             "creditorsotherthanconvertibledebt"
                                             ], True)
            debt = debt['total_assets']
        else:
            debt = debt['primary_assets']

        xbrl_parser.xbrl_extractor_sample.debt_equity_data.append(
            [company_number, debt, equity])

        log.debug(
            'Company - {} Debt - {}, Equity - {}'.format(company_number, debt, equity))
    except:

        xbrl_parser.xbrl_extractor_sample.debt_equity_data.append(
            [company_number, 0., 0.])

        log.error(
            'Error processing Company - {} '.format(company_number))



def dump_companies_with_account_data():

    company_numbers = get_companies_with_account_data()
    df = pd.DataFrame(company_numbers)

    df.to_csv('../data/companies_with_accounts.csv', header=False, index=False)

if __name__ == '__main__':
    extract_from_xbrl()
    # dump_companies_with_account_data()

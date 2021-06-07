import datetime

from pymongo import MongoClient


mongo_host = ""
mongo_db = ""
mongo_collection = ""

# TODO: Shared config?
servertype = ""


def report_mongo(host, test_groups, elapsed_time, log):
    """Write the test results to mongo database"""
    if mongo_host and mongo_db and mongo_collection:
        groups = test_groups.copy()
        groups.pop('total')
        document = {
            'host': host,
            'date': datetime.datetime.utcnow(),
            'server': servertype,
            'elapsed_time': elapsed_time,
            'tests': {
                'total': test_groups['total'],
                'failures': len(log['failures']),
                'errors': len(log['errors']),
                'timeouts': len(log['timeouts']),
                'skipped': len(log['skipped']),
                'success': len(log['success'])
            },
            'groups': groups,
            'results': log
        }
        mc = MongoClient(mongo_host)
        db = mc[mongo_db]
        tests = db[mongo_collection]
        result = tests.insert_one(document)
        return result.inserted_id
    else:
        return None

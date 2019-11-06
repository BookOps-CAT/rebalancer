"""
Sierra export parser
"""
import csv

from datastore import session_scope, Branch
from datastore_transactions import insert_or_ignore


def sierra_export_reader(fh):
    with open(fh, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        # skip header
        reader.__next__()

        for row in reader:
            yield row

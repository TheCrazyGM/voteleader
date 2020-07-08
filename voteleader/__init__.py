import os
import dataset

db = dataset.connect('sqlite:///holybread.db')
voter = os.environ['VOTER_ID']
wif = os.environ['VOTER_WIF']

# Encode as JSON for easy updating
from collections import OrderedDict


AUDN_CODES = OrderedDict({
    None: (1, 'Error'),
    'a': (2, 'Adult'),
    'j': (3, 'Juvenile'),
    'y': (4, 'Young adult')
})

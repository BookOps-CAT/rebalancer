# create and encode as JSON in the future for easy updating

STATUS_CODES = {
    None: (1, 'error'),
    '-': (2, 'bvailable'),
    'i': (3, 'at bindery'),
    'f': (4, 'being Filmed'),
    'n': (5, 'billed'),
    'k': (6, 'check w/staff'),
    'c': (7, 'closed branch'),
    'd': (8, 'damaged'),
    'z': (9, 'disputed item'),
    's': (10, 'en route'),
    '%': (11, 'ILL returned'),
    't': (12, 'in transit'),
    '$': (13, 'lost and paid'),
    'l': (14, 'lost inventory'),
    'm': (15, 'missing'),
    'x': (16, 'MML request'),
    'b': (17, 'new-in process'),
    'p': (18, 'non-cirulating'),
    'e': (19, 'on exibit'),
    '!': (20, 'on holdshelf'),
    'j': (21, 'overflow'),
    'h': (22, 'phone request'),
    'v': (23, 'preservation'),
    'y': (24, 'staff outreach'),
    '~': (25, 'staff use'),
    'g': (26, 'storage'),
    'u': (27, 'temporarily unavailable'),
    'o': (28, 'use in library'),
    'w': (29, 'withdrawn')
}
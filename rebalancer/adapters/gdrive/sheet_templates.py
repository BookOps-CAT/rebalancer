from data.branches import BRANCH_CODES


def branch_validation(tab_id):
    values = [
        {"userEnteredValue" : code} for code in BRANCH_CODES.keys() if code is not None]

    return {
        "range": {
            "sheetId": tab_id,
            "startRowIndex": 1,
            "startColumnIndex": 6,
            "endColumnIndex": 7,
        },
        "rule": {
            "condition": {
                "type": 'ONE_OF_LIST',
                "values": values
            },
            "inputMessage": 'invalid branch code',
            "strict": True,
            "showCustomUi": True
        }
    }


def conditional_formatting(tab_id):
    return {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [
                    {
                        "sheetId": tab_id,
                        "startRowIndex": 1,
                        "startColumnIndex": 6,
                        "endColumnIndex": 7
                    }
                ],
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_EQ",
                        "values": [
                            {
                                "userEnteredValue": "no"
                            }
                        ]
                    },
                    "format": {
                        'backgroundColor':
                            {
                                'red': 0.95686275,
                                'green': 0.78039217,
                                'blue': 0.7647059,
                            }
                    }
                }
            },
            "index": 0
        }
    }


# needs permission set
# and needs area protection

def shopping_cart_template(tab_id):
    """
    encodes properies of Google Sheet tab
    args:
        tab_id: string, tab (sheet id)
    returns:
        body: dictionary, request body
    """

    return {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": tab_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 0.64313725,
                                "green": 0.76078431,
                                "blue": 0.95686275
                            },
                            "horizontalAlignment": "CENTER",
                            "textFormat": {
                                "fontSize": 10,
                                "bold": True
                            }
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                }
            },
            {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': tab_id,
                        'gridProperties': {
                            'frozenRowCount': 1
                        },
                    },
                    'fields': 'gridProperties.frozenRowCount'
                },
            },
            {
                "setDataValidation": branch_validation(tab_id)
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": tab_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 1
                    },
                    "properties": {
                        "pixelSize": 150
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": tab_id,
                        "dimension": "COLUMNS",
                        "startIndex": 1,
                        "endIndex": 2
                    },
                    "properties": {
                        "pixelSize": 250
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": tab_id,
                        "dimension": "COLUMNS",
                        "startIndex": 2,
                        "endIndex": 3
                    },
                    "properties": {
                        "pixelSize": 300
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": tab_id,
                        "dimension": "COLUMNS",
                        "startIndex": 3,
                        "endIndex": 4
                    },
                    "properties": {
                        "pixelSize": 150
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": tab_id,
                        "dimension": "COLUMNS",
                        "startIndex": 4,
                        "endIndex": 5
                    },
                    "properties": {
                        "pixelSize": 200
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": tab_id,
                        "dimension": "COLUMNS",
                        "startIndex": 5,
                        "endIndex": 6
                    },
                    "properties": {
                        "pixelSize": 200
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": tab_id,
                        "dimension": "COLUMNS",
                        "startIndex": 6,
                        "endIndex": 7
                    },
                    "properties": {
                        "pixelSize": 80
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": tab_id,
                        "dimension": "COLUMNS",
                        "startIndex": 7,
                        "endIndex": 8
                    },
                    "properties": {
                        "pixelSize": 80
                    },
                    "fields": "pixelSize"
                }
            },
        ],
        'includeSpreadsheetInResponse': False,
        'responseIncludeGridData': False
    }

from data.branches import BRANCH_CODES
from data.editors import EDITORS


def format_row(tab_id, row_no):
    return {
        "repeatCell": {
            "range": {
                "sheetId": tab_id,
                "startRowIndex": row_no,
                "endRowIndex": row_no + 1,
                "startColumnIndex": 0,
                "endColumnIndex": 6
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.7176471,
                        "green": 0.88235295,
                        "blue": 0.8039216
                    },
                    "horizontalAlignment": "LEFT",
                    "textFormat": {
                        "fontSize": 10,
                        "bold": True
                    }
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
        }
    }


def cat_headings_formating(tab_id, row_nos):
    return {
        "requests": [format_row(tab_id, n) for n in row_nos]
    }


def branch_validation(tab_id, locations_number):
    values = [
        {"userEnteredValue" : f"=Locations!$A$1:$A${locations_number}"}]

    return {
        "range": {
            "sheetId": tab_id,
            "startRowIndex": 1,
            "startColumnIndex": 7,
            "endColumnIndex": 8,
        },
        "rule": {
            "condition": {
                "type": 'ONE_OF_RANGE',
                "values": values
            },
            "inputMessage": 'invalid branch code',
            "strict": True,
            "showCustomUi": True
        }
    }


def shopping_cart_data_tab_template(tab_id):
    """
    Encodes properies of Google Sheet tab
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
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": tab_id,
                                "startRowIndex": 1,
                                "startColumnIndex": 7,
                                "endColumnIndex": 8
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "NOT_BLANK",
                                "values": []
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
            },
            {
                "setDataValidation": branch_validation(tab_id)
            },
            {
                "addProtectedRange": {
                    "protectedRange": {
                        "range": {
                            "sheetId": tab_id,
                            "endColumnIndex": 0,
                            "endColumnIndex": 7
                        },
                        "description": "admin edits only",
                        "warningOnly": False,
                        "requestingUserCanEdit": False,
                        "editors": EDITORS
                    }
                }
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
                        "pixelSize": 80,
                        "hiddenByUser": True
                    },
                    "fields": "pixelSize, hiddenByUser"
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

from googleapiclient import discovery


from adapters.gdrive.sheet_templates import shopping_cart_template, cat_headings_formating


def create_sheet(creds, sheet_name, tabs=[]):
    """
    creates google spreadsheet in specified folder
    args:
        creds: instance of google.oauth2.credentials.Credentials class
        sheet name: string, name of Google sheet
        tabs: list, list of sheet tabs to be created
    returns:
        sheet_id: string, id of newly created Google Sheet
    """

    service = discovery.build('sheets', 'v4', credentials=creds)
    sheet_props = []
    for name in tabs:
        sheet_props.append(
            dict(
                properties=dict(title=name)))

    spreadsheet_body = {
        'sheets': sheet_props,
        'properties': {
            'title': sheet_name,
            'locale': 'en',
            'autoRecalc': 'ON_CHANGE',
            'timeZone': 'America/New_York'
        }
    }

    # create spreadsheet
    request = service.spreadsheets().create(
        body=spreadsheet_body)
    response = request.execute()

    return response['spreadsheetId']


def file2folder(creds, parent_id, file_id):
    """
    move file with provided id to appropriate folder
    args:
        auth: instance of google.oauth2.credentials.Credentials class
        parent_id: string, Google Drive folder id
        file_id: string, Google Drive document id
    returns:
        boolean: True if operation successful, False if not
    """

    service = discovery.build('drive', 'v3', credentials=creds)
    file = service.files().get(
        fileId=file_id,
        fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))

    # Move the file to the new folder
    response = service.files().update(
        fileId=file_id,
        addParents=parent_id,
        removeParents=previous_parents,
        fields='id, parents').execute()

    try:
        if response['parents'] == [parent_id]:
            return True
        else:
            return False
    except KeyError:
        return False


def append2sheet(creds, sheet_id, tab_name, data):
    """
    appends data to Google sheet with provided id
    args:
        creds: instance of google.oauth2.credentials.Credentials class
        sheet_id: string
        data: list of lists for each row
    returns:
        results: dictionary, Google API response
    """

    service = discovery.build('sheets', 'v4', credentials=creds)
    value_input_option = 'RAW'
    body = {
        'values': data,
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=sheet_id, range=tab_name,
        valueInputOption=value_input_option, body=body).execute()

    return result


def customize_shopping_sheet(creds, sheet_id, tabs):
    """
    applies structure and formatting to the shopping sheet
    args:
        creds: instance of google.oauth2.credentials.Credentials class
        sheet_id: string, Google Sheet id
    """

    service = discovery.build('sheets', 'v4', credentials=creds)

    header = [
        'category', 'author', 'title', 'call number',
        'publication', 'subject', 'item #', 'new branch'
    ]

    value_input_option = 'RAW'

    # create tabs
    for tab in tabs:
        body = {
            'values': [header]
        }
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id, range=tab,
            valueInputOption=value_input_option, body=body).execute()

    # get tab id and loop
    request = service.spreadsheets().get(
        spreadsheetId=sheet_id, ranges=tabs, includeGridData=False)
    response = request.execute()
    tab_ids = [
        sheet['properties']['sheetId'] for sheet in response['sheets']]

    # customize the look & behavior of each sheet
    for tab_id in tab_ids:
        request_body = shopping_cart_template(tab_id)

        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body=request_body).execute()


def update_categories_formatting(creds, sheet_id, tabs, row_nos):
    service = discovery.build('sheets', 'v4', credentials=creds)
    request = service.spreadsheets().get(
        spreadsheetId=sheet_id, ranges=tabs, includeGridData=False)
    response = request.execute()
    tab_ids = [
        sheet['properties']['sheetId'] for sheet in response['sheets']]

    # customize the headings of each sheet
    for tab_id in tab_ids:
        request_body = cat_headings_formating(tab_id, row_nos)
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body=request_body).execute()


def get_values(creds, sheet_id, values_range):
    service = discovery.build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=sheet_id, range=values_range).execute()

    values = result.get('values', [])

    return values


def get_properties(creds, sheet_id, values_range):
    service = discovery.build('sheets', 'v4', credentials=creds)
    includeGridData = True
    request = service.spreadsheets().get(
        spreadsheetId=sheet_id, ranges=values_range,
        includeGridData=includeGridData)
    response = request.execute()
    return response




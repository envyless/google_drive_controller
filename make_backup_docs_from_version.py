# -*- coding: utf-8 -*-

import __future__, sys

import io
from googleapiclient.discovery import build
#from googleapiclient.http import MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors
#from apiclient import errors


    # ...
    ## ---- download from file id(live folder)   : 0BxvW6_LMRmxDcFhSU2h2eXY2YUE (live)   
    # https://developers.google.com/drive/api/v3/about-auth
    # https://developers.google.com/drive/api/v3/reference/files/copy
    ## mimeType = https://developers.google.com/drive/api/v3/mime-types
    ### ------- find name contain hello  https://developers.google.com/drive/api/v3/search-files


# succes versions of this task
recorded_version = []

def load_and_write_version():
    with open('succes_versions.txt', 'r') as filehandle:
            for line in filehandle:
                # remove linebreak which is the last character of the string
                currentPlace = line[:-1]
                # add item to the list
                recorded_version.append(currentPlace)


def copy_file(service, origin_file_id, copy_title, folder_id=0):
  """Copy an existing file.

  Args:
    service: Drive API service instance.
    origin_file_id: ID of the origin file to copy.
    copy_title: Title of the copy.

  Returns:
    The copied file if successful, None otherwise.
  """
  copied_file = {'name': copy_title}
  if(folder_id!=0):
      copied_file['parents'] = [folder_id]

  try:
    return service.files().copy(
        fileId=origin_file_id, body=copied_file).execute()
  except errors.HttpError as error:
    print(error)
    return None


if __name__ == "__main__":
    # version from must arg
    version = '1.0.20112401'
    # arguments 
    num_of_arg = len(sys.argv)
    if num_of_arg > 1:
        version = str(sys.argv[1])
        print ("version : ",version)    
        sys.argv.remove(version)    
    else:
        print ("args it must be docs version code like 1.0.20072301")
        sys.exit(0)

    try :
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None    

    #scope setting you can check in "https://developers.google.com/drive/api/v3/about-auth"
    SCOPES = 'https://www.googleapis.com/auth/drive'
    store = file.Storage('storage.json')
    creds = store.get()

    if not creds or creds.invalid:
        print("make new storage data file ")
        flow = client.flow_from_clientsecrets('client_secret_drive.json', SCOPES)
        creds = tools.run_flow(flow, store, flags) \
                if flags else tools.run(flow, store)

    drive_service = build('drive', 'v3', http=creds.authorize(Http()))
    
    # make parent folder
    file_metadata = {
        'name': 'backup-{0}'.format(version),
        'parents' : ["0BxvW6_LMRmxDcFhSU2h2eXY2YUE"],
        'mimeType': 'application/vnd.google-apps.folder',        
    }
    folder_object = drive_service.files().create(body=file_metadata,  # pylint: disable=maybe-no-member
                                        fields='id').execute()
    print ('Folder ID: %s' % folder_object.get('id'))

    # arrays for copy items
    filenames = []
    fileids = []
    parent_folder = folder_object.get('id')	    
    fileids = []

    # make query and recieve respones
    query="name contains '{name}' and not name contains 'backup' and mimeType='{mimeType}'".format(name=version, mimeType='application/vnd.google-apps.spreadsheet')

    # do query
    while True:        
        response = drive_service.files().list(q=query, fields='nextPageToken, files(id, name)').execute()  # pylint: disable=maybe-no-member
        for file in response.get('files', []):
            # Process change
            file_name = file.get('name')
            file_id = file.get('id')

            # file caching for copy
            filenames.append(file_name)
            fileids.append(file_id)

            print ('Found file: %s (%s)' % (file_name, file_id))            
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    
    done_file_name = []

    # file copy
    for i in range(0, len(filenames)):
        # make new copy name
        copy_title = filenames[i].replace(version, 'backup-{0}'.format(version))
        copy_title = copy_title.replace(u"의 사본", "")
        
        # already done file, must skip
        if done_file_name.__contains__(copy_title):
            continue

        # do copy and add done
        print(copy_title)
        copy_file(drive_service, fileids[i], copy_title, parent_folder)
        done_file_name.append(copy_title)

        
    recorded_version.append(version)
    with open('succes_versions.txt', 'w') as filehandle:
            for listitem in recorded_version:
                filehandle.write('%s\n' % listitem)

    print(" Congraturation it's succes to backup docks {0}!! ".format(version))

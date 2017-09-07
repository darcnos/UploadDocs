import base64, requests, json, os, glob
from pytz import timezone
from datetime import datetime

est = timezone('US/Eastern')
myheaders = {'content-type': 'application/json'}

fbheaders = {'content-type': 'application/json'}
img_dir = os.path.dirname(os.path.realpath(__file__))
outgoing = img_dir + '/sub' 
global siteurl

def login():
    global siteurl
    """Logs into the specified URL as 'maximus', returns a guid"""
    siteurl = 'https://montcopawebdocs.filebound.com'
    u = 'dcarson'
    p = input('enter a password: ')
    data = {
        'username': u,
        'password': p
    }

    login = 'https://applications.filebound.com/v3/login/?fbsite=https://' + siteurl
    try:
        r = requests.post(login, data)
        guid = r.json()
        return guid
    except requests.exceptions.Timeout:
        print('Connection timed out. Please try again.')
    except requests.exceptions.TooManyRedirects:
        print('Too many redirects. Check your URL and try again.')
    except requests.exceptions.RequestException as e:
        print('Catastrophic error. Bailing.')
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    print('Running login code.')
    guid = login()
    #print(guid)


#Pull a file template from FileBound Server


NEWFILE_string = 'https://applications.filebound.com/v3/empty?template=file&fbsite={}&guid={}'.format(siteurl, guid)
NEWDOC_string = 'https://applications.filebound.com/v3/empty?template=document&fbsite={}&guid={}'.format(siteurl, guid)
inc_filetemplate = json.loads(requests.get(NEWFILE_string).text)
filetemplate = inc_filetemplate
r = requests.get(NEWDOC_string)
inc_doctemplate = json.loads(requests.get(NEWDOC_string).text)
doctemplate = json.loads(requests.get(NEWDOC_string).text)



#Generate the file list from output dir
filelist = [filename for filename in glob.glob(outgoing + '\*.*')]
print(filelist)


#For each of the docs in the list...
for doc in filelist:
    base = os.path.basename(doc)
    ext = os.path.splitext(base)[1][1:]
    #Read the current file, convert to base64 and PUT it on the server
    with open(doc, 'rb') as current_doc:
        docstring = base64.b64encode(current_doc.read()).decode('utf-8')
        put_data = json.dumps(filetemplate)
        NEWFILE_string = 'https://applications.filebound.com/v3/projects/25/files?fbsite={}&guid={}'.format(siteurl, guid)
        try:
            #Create the file
            r = requests.put(NEWFILE_string, put_data, headers=fbheaders)
            fileId = r.text
            #print(datetime.now(est).strftime("%m/%d/%Y %H:%M:%S") + ' - Saved FileID '+ fileId)
            
            FILE_PUT_string = 'https://applications.filebound.com/v4/files?fbsite={}&guid={}'.format(siteurl, guid)
            DOC_PUT_string = 'https://applications.filebound.com/v4/documents/{}/?fbsite={}&guid={}'.format(fileId, siteurl, guid)
            
            currentdoc_template = doctemplate
            currentdoc_template['binaryData'] = docstring
            currentdoc_template['extension'] = ext
            post_object = json.dumps(currentdoc_template)
            
            docpost_r = requests.put(DOC_PUT_string, post_object, headers=myheaders)
            print(datetime.now(est).strftime("%m/%d/%Y %H:%M:%S") + ' - Saved DocID ' + docpost_r.text)
            #print(docpost_r)



        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

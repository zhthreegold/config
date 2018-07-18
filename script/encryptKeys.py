import os,re,yaml,requests
from StringIO import StringIO

dir_path="./safedelete_data"
encrypted_dir_path="./safedelete_encrypted"
key_file_path="./keys"

encryptedKeys=set()


# # For IGNORE keys
# def processFile(input_stream):
#     output_stream = ""
#     lines = input_stream.readlines()
#     for line in lines:
#         matchObj = re.match(r'^##\s*IGNORE\s*(.*)\s*$',line)
#         if matchObj:
#             output_stream += matchObj.group(1) + 'IGNORE\n'
#         else:
#             output_stream += line
#     return StringIO(output_stream)
#
# def yaml2Dict(file_name):
#     with open(file_name,'r') as yaml_file:
#         try:
#             #One yaml file may contain multiple documents, i.e. --- # another doc
#             #We should have one doc per file, but application-*.yml may have more than
#             #one doc. We only check the first non-None doc in each file.
#             docs = yaml.load_all(processFile(yaml_file))
#             data = {}
#             for doc in docs:
#                 if doc:
#                     data = doc
#                     break
#             return True, data
#         except yaml.YAMLError as e:
#             print(file_name + ' is invalid yaml: %s' % e)
#     return False,{}

def loadKeys():
    with open(key_file_path) as myFile:
        lines = myFile.readlines()
        for line in lines:
            encryptedKeys.add(line[:-1])
            #print line[:-1]

def encryptKeys():
    for f in os.listdir(dir_path):
        file_path = dir_path + '/' + f

        matchFile_properties = re.match(r'(.+)-(.+)\.properties', f)
        matchFile_yml = re.match(r'(.+)-(.+)\.yml', f)

        if matchFile_properties:
            with open(file_path) as myFile:
                print "\n",f,"\n"
                lines = myFile.readlines()
                lineNum=0
                for line in lines:
                    matchObj_properties = re.match(r'([^=\s]+)\s*=(.*)',line)
                    if matchObj_properties:
                        key=matchObj_properties.group(1)
                        value=matchObj_properties.group(2)
                        #print matchObj.group(1)
                        if key in encryptedKeys:
                            print key, value
                            lines[lineNum]=key+'={cipher}'+encrypt(value) + '\n'
                    lineNum+=1
                with open(encrypted_dir_path+'/'+f,'w') as myFile_encrypt:
                    myFile_encrypt.writelines(lines)
        # if matchFile_yml:
        #     ret, data = yaml2Dict(file_path)
        #     if ret:
        #         for key, value in data.iteritems():
        #             print str(key)
        #             print "hi"
        #             print str(value)
        #             #matchObj_yml = re.match(r'([^:\s]+\s*):.*\{cipher\}',value)
        #             #if matchObj_yml:
        #             #     encryptedKeys.add(key)

def encrypt(value):
    url = 'http://localhost:8888/encrypt'
    url2 = 'http://localhost:8888/env'
    headers = {'Content-Type': 'text/plain'}
    data = value
    response = requests.post(url, headers=headers, data=data)
    #response = requests.get(url2, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return "FAIL TO ENCRYPT"



if __name__=="__main__":
    loadKeys()
    encryptKeys()

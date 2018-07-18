import os,re,yaml
from StringIO import StringIO

dir_path="./configurations"
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

def findEncryptedKeys():
    for f in os.listdir(dir_path):
        file_path = dir_path + '/' + f

        matchFile_properties = re.match(r'(.+)-(.+)\.properties', f)
        matchFile_yml = re.match(r'(.+)-(.+)\.yml', f)

        if matchFile_properties:
            with open(file_path) as myFile:
                #print f
                lines = myFile.readlines()
                for line in lines:
                    matchObj_properties = re.match(r'([^=\s]+)\s*=.*\{cipher\}.*',line)

                    if matchObj_properties:
                        #print matchObj.group(1)
                        encryptedKeys.add(matchObj_properties.group(1))

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


    for encryptedKey in encryptedKeys:
        print encryptedKey

if __name__=="__main__":
    findEncryptedKeys()

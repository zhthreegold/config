#!/usr/bin/env python



import os,sys,re,json,yaml
from StringIO import StringIO

#Running directory
dir_path = os.getcwd()+'/data'

#Application object
class App:
    __name = ''
    __profiles = {}

    def __init__(self, name, profiles):
        self.__name = name
        self.__profiles = profiles

    def getName(self):
        return self.__name

    def getProfiles(self):
        return self.__profiles


# Helper Functions to convert different formats to dictionary

# A Helper function to parse .properties file, forked from pyjavaproperties 0.6
class Properties(object):

    def __init__(self, props=None):

        self._props = {}
        self._props_layer = {}

        self.othercharre = re.compile(r'(?<!\\)(\s*\=)|(?<!\\)(\s*\:)')
        self.othercharre2 = re.compile(r'(\s*\=)|(\s*\:)')
        self.bspacere = re.compile(r'\\(?!\s$)')

    def __str__(self):
        s='{'
        for key,value in self.__props.items():
            s = ''.join((s,key,'=',value,', '))

        s=''.join((s[:-2],'}'))
        return s

    def load(self, stream):
        lines = stream.readlines()
        lineno=0
        i = iter(lines)

        for line in i:
            lineno += 1
            line = line.strip()
            # Skip null lines
            if not line: continue
            # Skip lines which are comments
            if line[0] in ('#','!'): continue
            escaped=False
            sepidx = -1
            flag = 0
            m = self.othercharre.search(line)
            if m:
                first, last = m.span()
                start, end = 0, first
                flag = 1
                wspacere = re.compile(r'(?<![\\\=\:])(\s)')
            else:
                if self.othercharre2.search(line):
                    wspacere = re.compile(r'(?<![\\])(\s)')
                else:
                    wspacere = re.compile(r'(\s)')

                start, end = 0, len(line)
            m2 = wspacere.search(line, start, end)
            if m2:
                first, last = m2.span()
                sepidx = first
            elif m:
                first, last = m.span()
                sepidx = last - 1

            while line[-1] == '\\':
                # Read next line
                nextline = i.next()
                nextline = nextline.strip()
                lineno += 1
                # This line will become part of the value
                line = line[:-1] + nextline

            # Now split to key,value according to separation char
            if sepidx != -1:
                key, value = line[:sepidx], line[sepidx+1:]
            else:
                key,value = line,''
            self.processPair(key, value)
        #return self._props
        return self._props_layer

    def insertChild(self, data, keys, index, value):
        if index >= len(keys):

            # the key is already assigned to a dictionary type value
            # but the new value is a non-dictionary type value
            if data and isinstance(data,dict):
                #TODO:
                raise TypeError, "Different types of value is assigned to key: {}".format('.'.join(keys))
            return value

        # the key is already assigned to a non-dictionary type value
        # but the new value is a dictionary type value
        if not isinstance(data,dict):
            #TODO:
            raise TypeError, "Different types of value is assigned to key: {}".format('.'.join(keys))
            #return value
        key = keys[index]
        if not key in data:
            data[key] = {}
        data[key] = self.insertChild(data[key], keys, index+1, value)
        return data

    # Process a (key, value) pair
    def processPair(self, key, value):

        oldkey = key

        # Create key intelligently
        keyparts = self.bspacere.split(key)

        strippable = False
        lastpart = keyparts[-1]

        if lastpart.find('\\ ') != -1:
            keyparts[-1] = lastpart.replace('\\','')

        elif lastpart and lastpart[-1] == ' ':
            strippable = True

        key = ''.join(keyparts)
        if strippable:
            key = key.strip()
            oldkey = oldkey.strip()

        value = self.unescape(value)

        # Patch from N B @ ActiveState
        curlies = re.compile("{.+?}")
        found = curlies.findall(value)

        for f in found:
            srcKey = f[1:-1]
            if self._props.has_key(srcKey):
                value = value.replace(f, self._props[srcKey], 1)

        self.insertChild(self._props_layer, key.split('.'), 0, value.strip())

        self._props[key] = value.strip()

    def unescape(self, value):

        # Reverse of escape
        newvalue = value.replace('\:',':')
        newvalue = newvalue.replace('\=','=')

        return newvalue
###class Properties end

# For IGNORE keys
def processFile(input_stream):
    output_stream = ""
    lines = input_stream.readlines()
    for line in lines:
        matchObj = re.match(r'^##\s*IGNORE\s*(.*)\s*$',line)
        if matchObj:
            output_stream += matchObj.group(1) + 'IGNORE\n'
        else:
            output_stream += line
    return StringIO(output_stream)

def properties2Dict(file_name):
    properties = Properties()
    with open(file_name, 'r') as properties_file:
        try:
            data = properties.load(processFile(properties_file))
            return True, data
        except TypeError as e:
            print(file_name + ' is invalid properties: %s' % e)
    return False, {}

def yaml2Dict(file_name):
    with open(file_name,'r') as yaml_file:
        try:
            #One yaml file may contain multiple documents, i.e. --- # another doc
            #We should have one doc per file, but application-*.yml may have more than
            #one doc. We only check the first non-None doc in each file.
            docs = yaml.load_all(processFile(yaml_file))
            data = {}
            for doc in docs:
                if doc:
                    data = doc
                    break
            return True, data
        except yaml.YAMLError as e:
            print(file_name + ' is invalid yaml: %s' % e)
    return False,{}

# When a key is a number, some parsers tread it as string
# some tread it as array index and some tread it as number
# So it is safer to convert all the non-string keys to string
def convertKey2Str(data):
    if isinstance(data, dict):
        for key, value in data.iteritems():
            if not isinstance(key, basestring):
                data[str(key)] = data.pop(key)
                key = str(key)
            convertKey2Str(data[key])

# convert dict to properites-like key e.g. a: b: value => a.b = value
def convert2PropertiesKey(data_old,data_new, key_new):
    if isinstance(data_old, dict):
        for key_old, value_old in data_old.iteritems():
            key_tmp = str(key_new)
            key_new = str(key_old) if key_new =='' else str(key_new)+'.'+str(key_old)
            convert2PropertiesKey(data_old[key_old], data_new, key_new)
            key_new = key_tmp
        return
    else:
        data_new[key_new] = data_old


def file2Dict(file_name, file_type):
    ret = True
    if not os.path.isfile(file_name):
        print "missing file %s" % file_name
        return False, {}
    if file_type == 'yml' or file_type == 'yaml':
        ret, data = yaml2Dict(file_name)
    elif file_type == 'properties':
        ret, data = properties2Dict(file_name)
    else:
        print "Hmm ... file_type: %s is not support"
        return True, {}
    # convert non-str key to string key
    if ret:
        convertKey2Str(data)
        data_tmp, key_tmp = {},''
        convert2PropertiesKey(data, data_tmp, key_tmp)
        data = data_tmp
    # if len(data) < 5:
    #     print data
    return ret, data


# Compare if two dictionaries have the same keys
# return a empty string if nothing is wrong
def compare(data_base, data_compare, key_path):
    ret = []
    if isinstance(data_base, dict):
        for key_base, value_base in data_base.iteritems():
            key_tmp = str(key_path)
            key_path = str(key_base) if key_path=='' else str(key_path)+'.'+str(key_base)
            if not data_compare is None and key_base in data_compare:
                ret += compare(data_base[key_base], data_compare[key_base],key_path)
            else:
                ret.append( "## IGNORE %s\n" % key_path )
            key_path = key_tmp
        return ret
    elif isinstance(data_compare, dict):
        ret.append( "## IGNORE %s\n" % key_path )
        return ret
    else:
        if data_compare is None or data_compare == "":
            print("empty/null value is not allowed for key: %s\n" % key_path)
        return ret


# Determine the file need to compare
def determineCompare_file(file_name, file_type, profile):
    return dir_path+'/'+file_name+'-'+profile+'.'+file_type


# Add all the keys into a dictionary
def addAll(data_new, data):
    for key, value in data_new.iteritems():
        if not key in data:
            data[key] = value
        else:
            if isinstance(value, dict):
                if isinstance(data[key], dict):
                    addAll(value, data[key])
                else:
                    data[key] = value


def run(app):
    print "\n[Checking application:  {0:16s}... ]".format(app.getName())

    #data_base holds all the keys in every files
    data_base = {}
    result =  True
    for profile, file_type in app.getProfiles().iteritems():
        file_compare = determineCompare_file(app.getName(), file_type, profile)
        ret, data = file2Dict(file_compare, file_type)
        if not ret:
            print "Error: Fail to convert file: %s content to Dictionary" %file_compare
            return False
        addAll(data, data_base)

    for profile, file_type in app.getProfiles().iteritems():
        file_compare = determineCompare_file(app.getName(), file_type, profile)
        ret, data_compare = file2Dict(file_compare, file_type)
        if data_compare:
            key_path = ""
            ignore_key_list = compare(data_base, data_compare, key_path)
            if ignore_key_list:
                ignore_keys = ""
                for ignore_key in sorted(ignore_key_list):
                    ignore_keys += ignore_key
                with open(file_compare,'a') as myFile:
                    myFile.write("\n### ignore properties\n"+ignore_keys)
                result = False
            print "{0:36s} Completed".format(file_compare)
    return result


# Scan the root directory to parse application information into a list
def parseFiles():
    apps_dic={}
    for f in os.listdir(dir_path):
        matchObj = re.match(r'(.+)-(.+)\.(.+)', f)
        if matchObj:
            app_name = matchObj.group(1)
            profile = matchObj.group(2)
            file_type = matchObj.group(3)

            if app_name in apps_dic:
                if profile in apps_dic[app_name]:
                    print "Error: There are more than one files for profile: {}-{}".format(app_name,profile)
                    return False, []
                apps_dic[app_name][profile] = file_type
            else:
                apps_dic[app_name] = {profile:file_type}
    apps = []
    for key,value in apps_dic.iteritems():
        apps.append(App(key,value))

    if apps:
        print "[Application(s)]"
        for app in apps:
            print "{}".format(app.getName())
    return True, apps


def runAll():
    ret = True
    ret, apps = parseFiles()
    if apps and ret:
        for app in apps:
            if not run(app):
                ret = False
    return ret


if __name__=="__main__":
    runAll()

import re, sys
dir_src = './csv/'
dir_target = './data/'
file_name = sys.argv[1]
print file_name
with open(dir_target+file_name+'.properties','w') as propertiesFile:
    condition = re.compile(r'\w+(,)[^\s]+')
    with open(dir_src+file_name+'.csv','r') as csvFile:
        lineNo = 0
        for line in csvFile:
            lineNo+=1
            m = condition.search(line)
            if m:
                i = m.start(1)
                #print line[:i], line[i+1:]
                newLine = line[:i] + '=' + line[i+1:]
                propertiesFile.write(newLine)
            else:
                print lineNo,': ',line

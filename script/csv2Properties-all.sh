declare -a env=("prod" "dev" "test" "int" "uat" "auto" "demo")
declare -a country=("ca" "us" "uk")

dir="./csv/"
for e in "${env[@]}"
do
    for c in "${country[@]}"
    do
        fileName="sysconfig-${e}_${c}"
        if [ -f "${dir}$fileName.csv" ]; then
            echo "csv2Properties $fileName"
            python csv2Properties.py $fileName
        fi
    done
done

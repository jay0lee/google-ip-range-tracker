#!/bin/bash

while read line; do
    url=$(echo $line | cut -d' ' -f1)
    arrURL=(${url//// })
    filename="ips/${arrURL[-1]}"
    rightnow=$(date)
    echo "Checking ${filename}..."
    curl -s -f -o "${filename}" --compressed "${url}"; result=$?; true
    if [ $result -ne 0 ]; then
        echo "${url} failed with $result!"
	continue
    fi
    jq --sort-keys . "${filename}" | tee "${filename}"
    echo "${filename}"
    cat "${filename}"
done < ip-urls.txt

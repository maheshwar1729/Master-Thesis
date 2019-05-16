#!/bin/sh


echo "execution started.."
echo -n "" > sample.txt



top -b -n 1 | grep 'chromedriver' > sample.txt

top -b -n1 | grep "chromedriver" | head -1 | awk '{print $9}' > sample.txt
while [ true ]; do
    sleep 1
    echo "running.."

    top -b -n 1 | grep 'chromedriver' >> sample.txt

done

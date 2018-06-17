#!/bin/sh 

# Use this script to update all the copyright years in the source code and
# documentation

# Usage:
# ./update_copyright.sh <vgc-root> <previous-year> <current-year>
#
# Example:
# ./vgc-dev-tools/update_copyright.sh vgc 2017 2018

# Note: individual authors should not forget to update their lines in the
# COPYRIGHT file whenever they contribute new code in a given year.

# Update the copyright notices of all *.h files in $1/libs/
find $1/libs -name "*.h" |
while read filename
do
    sed -i "s/Copyright $2 The VGC Developers/Copyright $3 The VGC Developers/g" $filename
done

# Update the copyright notices of all *.cpp files in $1/libs/
find $1/libs -name "*.cpp" |
while read filename
do
    sed -i "s/Copyright $2 The VGC Developers/Copyright $3 The VGC Developers/g" $filename
done

# Update the copyright notices of all *.h files in $1/apps/
find $1/apps -name "*.h" |
while read filename
do
    sed -i "s/Copyright $2 The VGC Developers/Copyright $3 The VGC Developers/g" $filename
done

# Update the copyright notices of all *.cpp files in $1/libs/
find $1/apps -name "*.cpp" |
while read filename
do
    sed -i "s/Copyright $2 The VGC Developers/Copyright $3 The VGC Developers/g" $filename
done

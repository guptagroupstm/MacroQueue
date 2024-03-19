#!/bin/sh

# Remove unnecessary files
if [ -e build ]; then
  rm -r build
fi

if [ -e dist ]; then
  rm -r dist
fi

# Create package
python setup.py sdist

echo "---------------------------------"
echo "Did you check version is correct?(yes/no)"
read ver
if [ $ver != "yes" ]; then
    exit
else
    echo "uploaded to pypi"
fi


# Select upload site
echo "Which repository do you want to upload (test/pypi)?"
read repo

if [ $repo = "pypi" ]; then
    echo "MacroQueue will be uploaded in pypi (not test). Do you really want to proceed? (yes/no)"
    read ans
    if [ $ans != "yes" ]; then
        exit
    else
        echo "uploaded to pypi"
        twine upload --repository pypi dist/*
    fi
else
    echo "uploaded to test"
    twine upload --repository testpypi dist/*
fi
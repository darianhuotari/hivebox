#!/bin/bash

APP_DIRECTORY=src
SCRIPT_DIR=$(pwd)

# Get version from src dir
cd ../$APP_DIRECTORY || exit
src_dir_ver=$(cat VERSION)

cd $SCRIPT_DIR
# Get version from root dir
cd .. || exit
root_ver=$(cat VERSION)

# Verify the versions match
if test "$src_dir_ver" != "$root_ver"; then
    echo "root version $root_ver and src version $src_dir_ver do not match; exiting...";
    exit 1;
fi

# Check if the root version file has been updated
if [ -z "$(git diff main -- VERSION)" ]; then
  echo "Version was not updated; please bump the version number. Exiting...";
  exit 1;
fi
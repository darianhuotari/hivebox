#!/bin/bash
# Please run this script from the root directory and not this scripts directory, or path resolution will fail.

APP_DIRECTORY=src

# Get version from src dir
cd $APP_DIRECTORY/ || exit
src_dir_ver=$(cat VERSION)

# Get version from root dir
root_ver=$(cat VERSION)

# Verify the versions match
if test "$src_dir_ver" != "$root_ver"; then
    echo "root version $root_ver and src version $src_dir_ver do not match; exiting...";
    exit 1;
fi

# Check if the root version file has been updated
if [ -z "$(git diff origin/main -- VERSION)" ]; then
  echo "Version was not updated; please bump the version number. Exiting...";
  exit 1;
fi
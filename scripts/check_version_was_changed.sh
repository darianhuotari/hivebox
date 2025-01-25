#!/bin/bash
# NOTE: Please run this script from the root directory and not this scripts directory, or path resolution will fail.

APP_DIRECTORY=src
TEST_DIRECTORY=tests
DOCKERFILE=.Dockerfile

# Get diff against main for applicable directories and files, and store in variables
CHANGES_APP_DIR=$(git diff origin/main -- "$APP_DIRECTORY")
CHANGES_TEST_DIR=$(git diff origin/main -- "$TEST_DIRECTORY")
CHANGES_DOCKERFILE=$(git diff origin/main -- "$DOCKERFILE")
CHANGES_INIT=$(git diff origin/main -- "__init__.py")

# If all variables are empty, no changes were detected, so we skip running the tests. We exit 0 so the test passes, since it's required to pass before merging to main
if [ -z "${CHANGES_APP_DIR}" ] && [ -z "${CHANGES_TEST_DIR}" ] && [ -z "${CHANGES_DOCKERFILE}" ] && [ -z "${CHANGES_INIT}" ]; then
  echo "No changes requiring these tests detected; exiting early...";
  exit 0;

fi

# Check if there was changes to files before running test
#if [ -z "$(git diff origin/main -- "$APP_DIRECTORY"/)" ]; then
#  echo "No changes detected in "$APP_DIRECTORY"/";
  #exit 0;

#fi



# Get version from src dir
cd "$APP_DIRECTORY"/ || exit
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
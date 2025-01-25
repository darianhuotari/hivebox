#!/bin/bash

APP_DIRECTORY=src
TEST_DIRECTORY=tests
SCRIPT_DIRECTORY=scripts
DOCKERFILE=.Dockerfile

# Get diff against main for applicable directories and files, and store in variables
# We may remove the script dir check if it causes issues later
CHANGES_APP_DIR=$(git diff origin/main -- "$APP_DIRECTORY")
CHANGES_TEST_DIR=$(git diff origin/main -- "$TEST_DIRECTORY")
CHANGES_DOCKERFILE=$(git diff origin/main -- "$DOCKERFILE")
CHANGES_INIT=$(git diff origin/main -- "__init__.py")
CHANGES_SCRIPT_DIR=$(git diff origin/main -- "$SCRIPT_DIRECTORY")

# If all variables are empty, no changes were detected, so we skip running the tests. We exit 0 so the test passes, since it's required to pass before merging to main
if [ -z "${CHANGES_APP_DIR}" ] && [ -z "${CHANGES_TEST_DIR}" ] && [ -z "${CHANGES_DOCKERFILE}" ] && [ -z "${CHANGES_INIT}" ] && [ -z "${CHANGES_SCRIPT_DIR}" ]; then
  echo "No changes requiring build and smoke tests were detected; exiting...";
  exit 0;

fi


sudo apt-get update
sudo apt-get -y install curl

docker build . -f .Dockerfile -t hivebox:local-ci
docker run -d -p 8000:8000 hivebox:local-ci

sleep 10

## curl --silent, --output to /dev/null, --write-out only the http status code
STATUSCODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/version)

if test "$STATUSCODE" -ne 200; then
    echo "/version endpoint call failed; exiting...";
    exit 1;
else
    echo "/version endpoint successfully responded with HTTP 200."
fi

#!/usr/bin/env bash

base_dir=$(dirname "$0");

# shellcheck source=.deploy/shared.sh
# shellcheck disable=SC1091
source "${base_dir}/shared.sh";

get_opts() {
	while getopts ":n:v:" opt; do
	  case $opt in
			n) export opt_project_name="$OPTARG";
			;;
			v) export opt_version="$OPTARG";
			;;
	    \?) __error "Invalid option -$OPTARG";
	    ;;
	  esac;
	done;
	return 0;
};

get_opts "$@";


PROJECT_NAME="${opt_project_name:-"${CI_PROJECT_NAME}"}";
BUILD_VERSION=${CI_BUILD_VERSION:-"1.0.0-snapshot"};
DOCKER_ORG="camalot";
tag="${DOCKER_ORG}/${PROJECT_NAME}";
FOLDER_NAME="MedalOverlay";

[[ -p "${PROJECT_NAME// }" ]] && __error "'-p' (project name) attribute is required.";
[[ -p "${BUILD_VERSION// }" ]] && __error "'-v' (version) attribute is required.";

mkdir -p "${WORKSPACE}/temp/";
mkdir -p "${WORKSPACE}/dist/";
cp -r "${WORKSPACE}/script" "${WORKSPACE}/temp/";
cp "${WORKSPACE}/ReadMe.md" "${WORKSPACE}/temp/script/";
cp "${WORKSPACE}/SendKeys.md" "${WORKSPACE}/temp/script/";


sed -i "s/Version = \"1.0.0-snapshot\"/Version = \"${BUILD_VERSION}\"/g" "${WORKSPACE}/temp/script/Medal_StreamlabsSystem.py";
sed -i "s/Version = \"1.0.0-snapshot\"/Version = \"${BUILD_VERSION}\"/g" "${WORKSPACE}/temp/script/update.py";

# Download the latest version of the updater
curl -sSL $(curl -s https://api.github.com/repos/camalot/chatbotscriptupdater/releases/latest \
| jq -r '.assets[] | select(.name|test("ApplicationUpater.Administrator")) | .browser_download_url') > ${WORKSPACE}/temp/script/applicationupdater.zip;

sleep 2;
cat ${WORKSPACE}/temp/script/applicationupdater.zip
mkdir -p ${WORKSPACE}/temp/script/libs/updater/
unzip -d ${WORKSPACE}/temp/script/libs/updater/ ${WORKSPACE}/temp/script/applicationupdater.zip;
sleep 2;
rm "${WORKSPACE}/temp/script/applicationupdater.zip";

mv "${WORKSPACE}/temp/script" "${WORKSPACE}/temp/${FOLDER_NAME}";
pushd . || exit 9;
cd "${WORKSPACE}/temp/" || exit 9;
pwd;
zip -r "${PROJECT_NAME}-${BUILD_VERSION}.zip" --exclude=@${WORKSPACE}/.zipignore -- *;
mv "${PROJECT_NAME}-${BUILD_VERSION}.zip" "${WORKSPACE}/dist/";
popd || exit 9;

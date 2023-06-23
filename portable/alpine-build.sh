#!/usr/bin/env sh

# This script builds a standalone statically linked musl binary
# from the root project. Its main sequence is:
#
# - install build dependencies for staticx + whatever python
#   requirements we desire to build locally (as opposed to wheel) -
#   we'll refer to these as 'static' requirements
# - install staticx to the root python
# - create a virtual environment
# - install non-static requirements via wheels
# - install static requirements by building them locally
# - produce a 'onefile' executable of the project using pyinstaller
# - convert the executable to a statically linked one using staticx

project="cloudy"
entrypoint="${project}/cloudy.py"
static_reqs=""
static_reqs_re=`echo $static_reqs | tr " " "|"`
static_reqs_build_deps=""

PIP_INSTALL="pip install --root-user-action=ignore --no-cache-dir"

set -xe

apk add --no-cache g++ musl-dev patchelf git make openssl $static_reqs_build_deps
$PIP_INSTALL -U wheel setuptools
$PIP_INSTALL scons
$PIP_INSTALL staticx

my_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
oldpath="`pwd`"
cd "$my_dir/.."

rm -rf .venv
python3 -m venv .venv
set +x; source .venv/bin/activate; set -x

# make sure static reqs are locally built (no wheels)
if test -n "$static_reqs"; then
  $PIP_INSTALL -r <(grep -iv -E $static_reqs_re requirements.txt)
  pip3 uninstall -y $static_reqs
  $PIP_INSTALL -I --no-binary :all: -r <(grep -i -E $static_reqs_re requirements.txt)
else
  $PIP_INSTALL -r requirements.txt
fi

# produce a 'onefile' executable
$PIP_INSTALL -I pyinstaller
rm -rf dist build
pyinstaller --onefile "${entrypoint}" -n "${project}"

set +x; deactivate; set -x

# make it portable using staticx
mkdir -p dist/static
staticx --loglevel INFO "dist/${project}" "dist/static/${project}"
cd "$oldpath"


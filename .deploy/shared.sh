#!/usr/bin/env bash

__print() {
	TCOLOR=$(if [[ ! -z "${1// }" ]]; then echo ";$1"; else echo ''; fi);
	COLOR="\\033[0${TCOLOR}m";
	NC='\033[0m';
	(>&2 echo -e "${COLOR}${*:2}${NC}");
}

__error() {
	__print 31 "${@:2}"
	exit 9;
}
__warning() {
	__print 33 "${@:2}"
}
__info() {
	__print 36 "${@:2}"
}

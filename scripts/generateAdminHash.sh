#!/bin/bash

if [ "x$1" == "x" ]; then
	echo "	Usage: $0 <admin Password>"
	exit
	fi

echo -n "$1" | sha256sum | cut -f1 -d' '

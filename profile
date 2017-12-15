if command -v greadlink > /dev/null; then
  readlink=greadlink
else
  readlink=readlink
fi

curdir=$(pwd)
cd $(dirname $($readlink -f "${BASH_SOURCE[0]}") )
THISDIR=$(pwd)
cd $curdir

export PATH=$PATH:$THISDIR/python
export PATH=$PATH:$THISDIR/bash


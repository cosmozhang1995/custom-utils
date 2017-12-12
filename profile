THISDIR=$(cd $(dirname $(readlink -f "${BASH_SOURCE[0]}") ) ; pwd )

export PATH=$PATH:$THISDIR/python
export PATH=$PATH:$THISDIR/bash


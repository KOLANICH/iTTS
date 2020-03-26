iTTS.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
===========
![GitLab Build Status](https://gitlab.com/KOLANICH/iTTS.py/badges/master/pipeline.svg)
[![TravisCI Build Status](https://travis-ci.org/KOLANICH/iTTS.py.svg?branch=master)](https://travis-ci.org/KOLANICH/iTTS.py)
![GitLab Coverage](https://gitlab.com/KOLANICH/iTTS.py/badges/master/coverage.svg)
[![Coveralls Coverage](https://img.shields.io/coveralls/KOLANICH/iTTS.py.svg)](https://coveralls.io/r/KOLANICH/iTTS.py)
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH/iTTS.py.svg)](https://libraries.io/github/KOLANICH/iTTS.py)

Just a kernel for Jupyter notebook speaking text from cells.

The work is based on https://github.com/takluyver/bash_kernel, which is licensed under [BSD 3-clause license](https://github.com/takluyver/bash_kernel/blob/master/LICENSE).

Limitations and ToDos
======================

* Currently it speaks only using system loudspeakers because speech-dispatcher (and its protocol) lacks the functionality to get the voice stream instead of speaking it.
* Currently lacks an abstraction layer to support different APIs, such as SAPI5 uniformly.
* Currently it lacks automatic language detection. `langdetect` is shit (in the sense its quality is too poor). `nltk` can be used for that once the issue with insecure way of providing pretrained models needed for it is solved.
* Currently it lacks autocompletion of the arguments of the magics.
* Currently it lacks hints on the magics.
* Currently it lacks autocompletion of words for usual text based on beginning of the sentence.
    * Markov models can be used
    * or maybe RNNs

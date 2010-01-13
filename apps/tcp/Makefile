###############
# Usage
###############
# Makefile to quickly build and run test files.
# Use:
# 	make - run all tests
# 	make units - run low-level function tests
# 	make funcs - run class scope tests
# 	make ingrs - run integrations
#	make clean - delete built tests and test output
#	make dist - make a distributable tarball
#	make image - link the library into a single file
#	make example - run a hello world script
#
# You can pass the FN=<regex> to match subsets of tests.
# Ex. make units FN=state_machin
#     make ingrs FN=net_tiny
#
# You can run a file without the test framework by:
#	make run FN=<regex>
# Ex. make run FN=z_test_me.repy
################

############
# Constants
###########
# the dist
REPYTAR=seattle_linux.tgz
# the untared dir
REPYDIR=seattle_repy

REPYPP=${REPYDIR}/repypp.py
ROOTDIR=tcp

# test
TESTDIR=tmp_test_dir
TESTS_SRC_DIR=tests
FN=[zne]_test_*
UNITS=${TESTS_SRC_DIR}/units
FUNCS=${TESTS_SRC_DIR}/functionals
INGRS=${TESTS_SRC_DIR}/integrations
RESTR_FN=restrictions.default

# image
IMAGEDIR=image

# dist
DISTDIR='.dist'

# example
EXAMPLEDIR=examples
EXAMPLE_SCRIPT=helloworld

#############
# Public Commands
#############

# Run through Test framework
all: cp_units cp_funcs cp_ingrs build test
units: cp_units build test
funcs: cp_funcs build test
ingrs: cp_ingrs build test

# Use to execute a single test file without framework.
# Ex. make run FN=<filename>
run: cp_units cp_funcs cp_ingrs build
	cd ${TESTDIR} && python repy.py ${RESTR_FN} *${FN}*

clean: 
	# test 
	rm -rf ${TESTDIR}
	for file in `ls *.repy`; do rm -f ${TESTS_SRC_DIR}/$${file}; done
	for file in `ls ${UNITS}/*`; do rm -f ${TESTS_SRC_DIR}/`basename $${file}`; done
	for file in `ls ${FUNCS}/*`; do rm -f ${TESTS_SRC_DIR}/`basename $${file}`; done
	for file in `ls ${INGRS}/*`; do rm -f ${TESTS_SRC_DIR}/`basename $${file}`; done
	
	# dist 
	rm -rf ${DISTDIR}
	rm -f ${ROOTDIR}.tgz
	rm -rf ${ROOTDIR}

	# image
	rm -rf ${IMAGEDIR}

# Links all the files into a single easily includable file
image:
	if [ ! -e ${IMAGEDIR} ]; then mkdir ${IMAGEDIR}; fi
	cat *.repy > ${IMAGEDIR}/${ROOTDIR}.repy
	sed -i 's/^\(include .*\)$$/#\1/' ${IMAGEDIR}/${ROOTDIR}.repy

# Makes a distributable version of the current code
dist: superclean
	# get all of the repo setup
	mkdir ${DISTDIR}
	cp -r * ${DISTDIR}

	# tar it
	mv ${DISTDIR} ${ROOTDIR} # rename as root dir
	tar czf ${ROOTDIR}.tgz ${ROOTDIR}
	rm -rf ${ROOTDIR}

example: image
	cp ${EXAMPLEDIR}/${EXAMPLE_SCRIPT}.repy ${IMAGEDIR}
	cd ${IMAGEDIR} && python ../${REPYPP} ${EXAMPLE_SCRIPT}.repy ${EXAMPLE_SCRIPT}
	cd ${IMAGEDIR} && python ../${REPYDIR}/repy.py ../${TESTS_SRC_DIR}/${RESTR_FN} ${EXAMPLE_SCRIPT}

################
# Private Commands
###############

# Run seattle's test script.  Test should be built first.
test: 
	cd ${TESTDIR} && python run_tests.py

# Builds all test files
# Takes FN as arg, ex. `make FN=*controller*` to build all files with glob.
build: repy
	cd ${TESTS_SRC_DIR} && ./build.sh ${TESTDIR} "*${FN}*"
	cp ${TESTS_SRC_DIR}/*.txt ${TESTDIR}
	cp ${TESTS_SRC_DIR}/restrictions.* ${TESTDIR}
	cp ${TESTS_SRC_DIR}/run_tests.py ${TESTDIR}
	cp ${REPYDIR}/*.py ${TESTDIR}

superclean: clean
	rm -rf ${REPYDIR}

# download repy
repy:   
	# Dowloading Repy...
	if [ ! -e ${REPYDIR} ]; then wget --no-check-certificate https://seattlegeni.cs.washington.edu/geni/download/flibble/${REPYTAR}; tar xzf ${REPYTAR}; rm -f ${REPYTAR}; fi
	# done.
	#

cp_units:
	cp ${UNITS}/* ${TESTS_SRC_DIR}
cp_funcs:
	cp ${FUNCS}/* ${TESTS_SRC_DIR}
cp_ingrs:
	cp ${INGRS}/* ${TESTS_SRC_DIR}

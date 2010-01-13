# the dist 
REPYTAR=seattle_linux.tgz
# the untared dir
REPYDIR=seattle_repy

# Repy and Repypp
REPY=${REPYDIR}/repy.py 
REPYPP=${REPYDIR}/repypp.py 

# Tcp over upd lib
TCP=tcp.repy 

# the example scripts and restrictions file
TCUP=OurRepyTCPBenchmark#.repy
PYTCP=PythonTCPBenchmark#.py
REPYTCP=RepyTCPBenchmark#.repy 

RESTR=restrictions.default

DIST=tcpdemo
DEMO=demo

download: repy tcp benchmarks restrictions

tcup: download
	# Running TCUP Benchmark...
	python ${REPYPP} ${TCUP}.repy ${TCUP}
	python ${REPY} ${RESTR} ${TCUP} -s &
	python ${REPY} ${RESTR} ${TCUP} -c 
        # done.
	#

# run it
repytcp: download
	# Running Repy TCP Benchmark...
	python ${REPYPP} ${REPYTCP}.repy ${REPYTCP}
	python ${REPY} ${RESTR} ${REPYTCP} -s &
	python ${REPY} ${RESTR} ${REPYTCP} -c
        # done.
	#

# run it
pytcp: download
	# Running Python TCP Benchmark...
	python ${PYTCP}.py -s &
	python ${PYTCP}.py -c
        # done.
	#

semiclean:
	rm -rf ${TCUP}* ${REPYTCP}* ${PYTCP}* ${RESTR}

clean: semiclean
	rm -rf ${TCP} ${REPYDIR} ${REPYTAR} ${DIST} '.${DIST}' ${DIST}.tgz

superclean: clean
	killall -9 python


dist: clean
	mkdir '.${DIST}'
	cp * '.${DIST}'
	mv '.${DIST}' ${DIST}
	tar czf ${DIST}.tgz ${DIST}
	rm -rf ${DIST}

restrictions:
	cp ../tests/restrictions.default .

benchmarks:
	cp ../../../../benchmarks/tcp/*py .

# download repy
repy:
	# Dowloading Repy...
	if [ ! -e ${REPYDIR} ]; then wget --no-check-certificate https://seattlegeni.cs.washington.edu/geni/download/flibble/${REPYTAR}; tar xzf ${REPYTAR}; fi
	rm -f ${REPYTAR}
	# done.
	#

# download tcp/udp
tcp:
	# Dowloading TCP over UDP...
	if [ ! -e ${TCP} ]; then wget --no-check-certificate https://seattle.cs.washington.edu/raw-attachment/wiki/TCUP/${TCP}; fi
	# done.
	#

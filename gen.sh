#!/bin/bash

timestamp=`date +"%Y%m%d-%H%M%S"`
#tar -zcvf syskit-0.1.tar.gz syskit-0.1 --exclude syskit-0.1/repo.openeuler.org
cd security-baseline
cd ..
mv security-baseline-0.1.1.tar.gz back/security-baseline-0.1.1.tar.gz-${timestamp}
tar -zcvf security-baseline-0.1.1.tar.gz  \
	--exclude=security-baseline/repo.openeuler.org \
	--exclude=security-baseline/old \
	security-baseline

echo ""
echo ""
echo ""
tar -tf security-baseline-0.1.1.tar.gz

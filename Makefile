all:
	nosetests --with-coverage --cover-inclusive \
		--cover-package=bt_lib,test #--cover-tests

clean:
	find bt_lib test -name "*.py[co]" -exec rm '{}' \;
	rm -f .coverage btsnoop.dump test.pyc

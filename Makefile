all:
	python-coverage -e
	python-coverage -x test.py
	python-coverage -m -r -o /usr/lib/python2.6,/usr/share/pyshared

clean:
	find bt_lib -name "*.py[co]" -exec rm '{}' \;
	rm -f .coverage btsnoop.dump

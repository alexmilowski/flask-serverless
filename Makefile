gcp-package:
	rm -rf build
	mkdir -p build/packages
	pip install . ./test -t build/packages
	cp test/gcp_main.py build/packages/main.py
	cd build/packages; zip -r ../gcp.zip *
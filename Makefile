test:
	pytest --html=reports/report.html --junitxml=reports/junit.xml
	mv modules/backend_tests/tests/reports/*.html reports/ || true
	mv modules/backend_tests/tests/reports/*.xml reports/ || true

docker-build:
	docker build -t asteroids-api-tests .

docker-run:
	docker run --rm asteroids-api-tests

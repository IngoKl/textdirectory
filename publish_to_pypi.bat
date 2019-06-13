del build
del dist
python setup.py sdist
python setup.py bdist_wheel
python setup.py bdist_wheel --universal
twine upload dist/*

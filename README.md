#TODO:
o 


python -m pip install --upgrade pip
python -m venv .venv
. .venv/Scripts/activate  or source .venv/Scripts/activate

ve() {
    python -m pip install --upgrade pip
    python -m venv .venv
    source .venv/Scripts/activate
}

pip install ipykernel jupyterlab matplotlib pandas numpy SQLAlchemy
mkdir requirements
pip freeze > requirements/production.txt
pip install autopep8 pep8 pylint
pip freeze > requirements/development.txt

Copy this two files
    pythoncom37.dll
    pywintypes37.dll

From
    D:\Projects\Python\cars_data\.venv\Lib\site-packages\pywin32_system32\

To
    D:\Projects\Python\cars_data\.venv\Lib\site-packages\win32

python -m ipykernel install --user --name=cars_data
python -m notebook

deactivate

jupyter kernelspec list
jupyter kernelspec uninstall unwanted-kernel


```
pipenv install ipykernel pywin32 jupyter matplotlib pandas numpy SQLAlchemy
pipenv install --dev pep8 autopep8 pylint
```
```
python -m ipykernel install --user --name=cars_data
```
### List Jupyter Kernels
```
jupyter kernelspec list
```


Copy this two files
    pythoncom37.dll
    pywintypes37.dll

From
    D:\Projects\Python\cars_data\.venv\Lib\site-packages\pywin32_system32\

To
    D:\Projects\Python\cars_data\.venv\Lib\site-packages\win32

### Launch Jupyter Notebook
```
python -m notebook
```

In Jupyter Notebook test where a specific package is imported from, for example matplotlib:
```
import matplotlib
print(matplotlib.__file__)
# cars_data

jupyter kernelspec list
jupyter kernelspec uninstall unwanted-kernel


```
pipenv install ipykernel pywin32 jupyter matplotlib beautifulsoup4 requests pandas numpy SQLAlchemy
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
    pythoncom36.dll
    pywintypes36.dll

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

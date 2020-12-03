**Activate the virtual Environment**

```
Source blockchain-env/bin/activate
```

**Install All Packages**
```
pip install -r requirements.txt
```

**Run the test**
Make sure to activate the virtual environment

```
python -m pytest backend/tests
```

**Runnig a Peer Instance**
Activate the virtual environment.

```
export PEER=True && python -m backend.app
```

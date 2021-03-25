# SMARTSexplore

![SMARTSexplore graph preview](https://user-images.githubusercontent.com/669103/112528427-6bf05e80-8da4-11eb-9dfc-e03f7db73664.png "SMARTSexplore graph preview")

Welcome to the code repository of SMARTSexplore, a web-based
interactive visual analysis app for the exploration of chemical
pattern networks. SMARTSexplore was designed and developed in the
context of a 2020/2021 master student project for the [Computational
Molecular Design
group](https://www.zbh.uni-hamburg.de/en/forschung/amd.html), Center
for Bioinformatics, University of Hamburg, Germany.

Note: *This README is copied and slightly adapted from the
documentation's user guide (see "Building documentation"). The steps
below are only available here for convenience.  Please refer to the
documentation for further instructions, as well as the full user guide
and the developer guide.*


# Installing the backend dependencies

SMARTSexplore requires Python 3.8 or later. After you've installed an
appropriate Python version, please create a new virtual environment,
then activate it:

```
python3 -m venv venv
source venv/bin/activate
```

Now, install the project and its dependencies:

```
python setup.py install
```


# Installing the frontend dependencies

For generating the frontend code, you need a working `npm`
installation.  We recommend using
[nvm](https://github.com/nvm-sh/nvm#install--update-script) to install
an isolated version of npm.

After doing so, install all dependencies via:

```
npm install
```

Then, build the frontend code:

```
npm run build
```


# Building documentation

After following the steps to install the backend and frontend
dependencies, you can generate browsable HTML documentation by first
installing the jsdoc package:

```
npm install -g jsdoc
```

Then building the documentation:

```
python setup.py build_sphinx
```

and opening the file `build/sphinx/html/index.html`. It includes a
user guide, a developer guide, and documentation for the backend and
frontend APIs.



# Running a SMARTSexplore instance

## Installing required external programs

Please refer to https://software.zbh.uni-hamburg.de for retrieving the
required programs listed below.

For making molecule uploads work in the frontend, please place
licensed versions of the following NAOMI programs into the `bin/`
folder:

* `mol2svg`
* `SMARTSMoleculeMatcher` (formerly known as `structure_preprocessor`)

If you wish to add your own SMARTS data, it's required you also place
the following NAOMI programs there:

* `SMARTScompare`
* `SMARTScompareViewer`


## Generating the backend data

To initialize the database, run

```
flask db init
```

Then, add all SMARTS libraries from the data folder:

```
flask smarts add_libraries data/*.smarts
```

Now, SMARTS-SMARTS subset edges need to be calculated and stored in the database:

```
flask smarts calculate_edges SubsetOfFirst
```

After doing so, let the software draw all SMARTS and SMARTS-SMARTS edges:

```
flask smarts draw_all_smarts
flask smarts draw_all_subsets
```

The backend data is now ready.


## Starting the server

After following the steps above, you can start the server via

```bash
flask run
```

and access the SMARTSexplore application at <http://localhost:5000>.

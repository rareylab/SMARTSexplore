[![Documentation status](https://readthedocs.org/projects/smartsexplore/badge/?version=latest&style=for-the-badge)](https://smartsexplore.readthedocs.io/en/latest/)

# SMARTSexplore

![SMARTSexplore graph preview](https://user-images.githubusercontent.com/669103/112528427-6bf05e80-8da4-11eb-9dfc-e03f7db73664.png "SMARTSexplore graph preview")

Welcome to the code repository of SMARTSexplore, a web-based
interactive visual analysis app for the exploration of chemical
pattern networks. SMARTSexplore was designed and developed in the
context of a 2020/2021 master student project for the [Computational
Molecular Design
group](https://www.zbh.uni-hamburg.de/en/forschung/amd.html), Center
for Bioinformatics, University of Hamburg, Germany.

Note: *This README is copied and slightly adapted from a part of the
documentation's user guide (see "Building documentation"). The steps
below are only available here for convenience.  Please refer to [the
documentation](https://smartsexplore.readthedocs.io/) for further
instructions, as well as the full user guide and the developer guide.*


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


# Running a SMARTSexplore instance

## Installing required external programs

Please refer to https://software.zbh.uni-hamburg.de for retrieving the
required programs listed below.

For making molecule uploads work in the frontend, please create and place licensed versions of the following NAOMI programs into the `bin/`
folder:

* `mol2svg`
* `SMARTSMoleculeMatcher` (formerly known as `structure_preprocessor`)

If you wish to add your own SMARTS data, it's required you also place
the following NAOMI programs there:

* `SMARTScompare`
* `SMARTScompareViewer`

# Configuration

When using a Linux system, go to the `__init__.py` in the smartsxeplore folder and remove the `.exe` from the SMARTSCOMPARE_PATH, SMARTSCOMPARE_VIEWER_PATH and MATCHTOOL_PATH.

## Generating the backend data

To initialize the database, run

```
flask db init
```

Then, add all SMARTS libraries from the data folder:

```
flask smarts add_libraries data/smarts/*.smarts
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

After following the steps above, you can start the backend-server via

```bash
flask run
```

and access the backend at <http://localhost:5000>.

To run the frontend-server execute

```bash
npm run serve
```

on another terminal. The frontend can be accessed at <http://localhost:8080>
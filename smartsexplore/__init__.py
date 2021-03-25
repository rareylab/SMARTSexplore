import os

from flask import Flask
from flask import render_template
from flask_compress import Compress

__all__ = ['database', 'molecules', 'parsers', 'util', 'create_app']


def create_app(test_config=None, instance_path=None) -> Flask:
    """
    Creates the SMARTSexplore Flask app. Configurable via a ``config.py`` file or the
    `test_config` parameter. Read the code for available options.

    :param test_config: An optional Flask config mapping to use for test purposes.
    :param instance_path: An optional override on the Flask instance path. Useful for testing.
    :return: A fully created and configured SMARTSexplore Flask app.
    """
    # Config setup
    app = Flask(__name__, instance_relative_config=True, instance_path=instance_path)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE='sqlite:///' + os.path.join(app.instance_path, 'db.sqlite'),

        SMARTSCOMPARE_PATH=os.path.join(app.root_path, '..', 'bin', 'SMARTScompare'),
        SMARTSCOMPARE_VIEWER_PATH=os.path.join(app.root_path, '..', 'bin', 'SMARTScompareViewer'),
        MATCHTOOL_PATH=os.path.join(app.root_path, '..', 'bin', 'SMARTSMoleculeMatcher'),
        MOL2SVG_PATH=os.path.join(app.root_path, '..', 'bin', 'mol2svg'),

        ALLOWED_MOLECULE_SET_EXTENSIONS=['smi', 'smiles'],
        MAX_UPLOADED_MOLECULE_NUMBER=250,

        STATIC_SMARTSVIEW_PATH=os.path.join(app.instance_path, 'static', 'smartsview'),
        STATIC_SMARTSVIEW_SUBSETS_PATH=os.path.join(app.instance_path, 'static', 'smartssubsets'),
        STATIC_MOL2SVG_MOLECULE_SETS_PATH=os.path.join(app.instance_path, 'static', 'molecule_sets')
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Add compression via flask-compress
    compress = Compress()
    compress.init_app(app)

    # App instance folder creation (if not present)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Database setup
    from smartsexplore.database import bp as db_blueprint, get_session, close_session
    app.teardown_appcontext(close_session)
    app.register_blueprint(db_blueprint)

    # SMARTS setup
    from smartsexplore.smarts import bp as smarts_blueprint
    app.register_blueprint(smarts_blueprint)

    # Molecules setup
    from smartsexplore.molecules import bp as molecules_blueprint
    app.register_blueprint(molecules_blueprint)

    # Routing setup
    @app.route('/')
    @app.route('/index')
    def index():
        return render_template('index.html')

    # Finished, return app object
    return app

# -*- coding: utf-8 -*-
from flask import Flask

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class App(object):
    def __init__(self, *args, **kwargs):
        self.app = Flask(__name__, instance_relative_config=True)
        self.app.config.from_object('config')
        self.app.config.from_pyfile('config.py')
        # config/xxx.py -- scence config
        # app.config.from_envvar('APP_CONFIG_FILE') # APP_CONFIG_FILE defined in start.sh

        db.init_app(self.app)

        from flask.ext.migrate import Migrate, MigrateCommand
        self.migrate = Migrate(self.app, db)

        from flask.ext.script import Manager, Shell
        self.manager = Manager(self.app)

        self.manager.add_command('db', MigrateCommand)

        def make_shell_context():
            from .admin.models import Admin
            from .cart.models import Cart
            from .category.models import Cat1, Cat2
            from .location.models import School, Building
            from .order.models import Order, Order_snapshot
            from .product.models import Product, Product_building, Snapshot 
            from .pic.models import File, Promotion
            from .user.models import User
            
            return dict(app=self.app,
                    db=db,
                    Admin=Admin,
                    Cart=Cart,
                    Cat1=Cat1,
                    Cat2=Cat2,
                    School=School,
                    Building=Building,
                    Order=Order,
                    Order_snapshot=Order_snapshot,
                    Product=Product,
                    Product_building=Product_building,
                    Snapshot=Snapshot,
                    File=File,
                    Promotion=Promotion,
                    User=User,
                    )
        self.manager.add_command('shell', Shell(make_context=make_shell_context))
        from .admin import adminbp
        self.app.register_blueprint(
                adminbp,
                url_prefix='/admin',
                )
        from .cart import cartbp 
        self.app.register_blueprint(
                cartbp,
                url_prefix='/cart',
                )
        from .category import categorybp 
        self.app.register_blueprint(
                categorybp,
                url_prefix='/category',
                )
        from .location import locationbp 
        self.app.register_blueprint(
                locationbp,
                url_prefix='/location',
                )
        from .order import orderbp
        self.app.register_blueprint(
                orderbp,
                url_prefix='/order',
                )
        from .product import productbp
        self.app.register_blueprint(
                productbp,
                url_prefix='/product',
                )
        from .user import userbp 
        self.app.register_blueprint(
                userbp,
                url_prefix='/user',
                )
        from .pic import picbp
        self.app.register_blueprint(
                picbp,
                url_prefix='/pic',
                )
        from .main import mainbp # pc-end
        self.app.register_blueprint(
                mainbp,
                )
        from .mbend import mobilebp # mobile-end
        self.app.register_blueprint(
                mobilebp,
                url_prefix='/m'
                # subdomain='m',
                )
        

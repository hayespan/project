#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import App, db
app = App()

with app.app.app_context():
    db.create_all()

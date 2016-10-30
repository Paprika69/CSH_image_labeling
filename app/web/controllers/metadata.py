# -*- coding: utf-8 -*-

from flask import render_template
from flask_classy import FlaskView, route


class HomeView(FlaskView):
    route_base = '/'

    @route('/')
    def index(self):
        return render_template('index.html')


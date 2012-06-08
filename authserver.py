#!/usr/bin/env python

# ##### BEGIN AGPL LICENSE BLOCK #####
# This file is part of SimpleMMO.
#
# Copyright (C) 2011, 2012  Charles Nelson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END AGPL LICENSE BLOCK #####

'''AuthServer
A server providing registration, authentication, and allows a user to get a list of their characters.
'''

# TODO: Write a function to pull in the docstrings from defined classes here and 
# append them to the module docstring

import json
import logging

from sqlalchemy.exc import IntegrityError

import tornado

import settings

from baseserver import BaseServer, SimpleHandler, BaseHandler

from elixir_models import User, session

class PingHandler(BaseHandler):
    def get(self):
        self.write("pong")

# TODO: Make an SQLUserController
# TODO: Make an SQLCharacterController

class RegistrationHandler(BaseHandler):
    '''RegistrationHandler creates Users.'''
    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        email = self.get_argument("email", "")

        if not username:
            return self.HTTPError(400, "A user name is required.")

        if not password:
            return self.HTTPError(400, "A password is required.")

        user = self.register_user(username, password, email=email)
        logging.info("User was %s" % user)
        if user:
            return self.write('Registration successful.')
        else:
            return self.HTTPError(401, "User already exists.")

    def register_user(self, username, password, email=None):
        user = User(username=username, password=password, email=email)
        try:
            session.commit()
        except IntegrityError:
            # User already exists.
            session.rollback()
            user = False
        return user


class AuthHandler(BaseHandler):
    '''AuthHandler authenticates a user and sets a session in the database.'''
    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        auth = self.authenticate(username, password)
        if auth:
            self.set_current_user(username)
            self.set_admin(username)
            self.write('Login successful.')
        else:
            raise tornado.web.HTTPError(401, 'Login Failed, username and/or password incorrect.')

    def authenticate(self, username, password):
        '''Compares a username/password pair against that in the database.
        If they match, return True.
        Else, return False.'''
        # Do some database stuff here to verify the user.
        user = User.query.filter_by(username=username, password=password).first()
        return True if user else False

    def set_admin(self, user):
        # Look up username in admins list in database
        # if present, set secure cookie for admin
        if user in settings.ADMINISTRATORS:
            self.set_secure_cookie("admin", 'true')
        else:
            self.clear_cookie("admin")

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", user)
        else:
            self.clear_cookie("user")

class LogoutHandler(BaseHandler):
    '''Unsets the user's cookie.'''
    def get(self):
        self.clear_cookie("user")

class CharacterHandler(BaseHandler):
    '''CharacterHandler gets a list of characters for the given user account.'''

    @tornado.web.authenticated
    def get(self):
        self.write(json.dumps(self.get_characters(self.get_current_user())))

    def get_characters(self, username):
        '''Queries the database for all characters owned by a particular username.'''
        return ['Graxnor', 'Rumtiddlykins']

if __name__ == "__main__":
    from tornado.options import options, define
    define("dburi", default='sqlite:///simplemmo.sqlite', help="Where is the database?", type=str)

    tornado.options.parse_command_line()
    dburi = options.dburi

    handlers = []
    handlers.append((r"/", lambda x, y: SimpleHandler(__doc__, x, y)))
    handlers.append((r"/ping", PingHandler))
    handlers.append((r"/register", RegistrationHandler))
    handlers.append((r"/login", AuthHandler))
    handlers.append((r"/logout", LogoutHandler))
    handlers.append((r"/characters", CharacterHandler))

    server = BaseServer(handlers)
    server.listen(settings.AUTHSERVERPORT)

    # Connect to the elixir db
    from elixir_models import setup
    setup(db_uri=dburi)

    user = User.query.filter_by(username=settings.DEFAULT_USERNAME, password=settings.DEFAULT_PASSWORD).first()
    if not user:
        User(username=settings.DEFAULT_USERNAME, password=settings.DEFAULT_PASSWORD)
        session.commit()

    print "Starting up Authserver..."
    server.start()

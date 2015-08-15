from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    my_session_factory = SignedCookieSessionFactory('itsaseekreet')
    config = Configurator(settings=settings, session_factory=my_session_factory)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('new_game', '/game/new')
    config.add_route('click', '/game/click')
    config.add_route('toggle_flag', '/game/toggle_flag')
    config.scan()
    return config.make_wsgi_app()

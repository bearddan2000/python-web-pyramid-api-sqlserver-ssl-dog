from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import settings
from model import Base, DogModel

engine = create_engine('{engine}://{username}:{password}@{host}/{db_name}'.format(
        **settings.SQLSERVER
    ), 
    echo=settings.SQLALCHEMY['debug']    
)

session_local = sessionmaker(
    bind=engine,
    autoflush=settings.SQLALCHEMY['autoflush'],
    autocommit=settings.SQLALCHEMY['autocommit']
)

def hello_world(request):
    return Response('Hello World!')

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

@view_config(renderer='json')
def handle_pop(request):
    db = next(get_db())

    dogs = db.query(DogModel).all()
    results = [
        {
            "breed": dog.breed,
            "color": dog.color
        } for dog in dogs]

    return {"count": len(results), "dog": results, "message": "success"}

if __name__ == '__main__':
    with Configurator() as config:
        config.add_route('hello', '/')
        config.add_route('dog', '/dog')
        config.add_view(hello_world, route_name='hello')
        config.add_view(handle_pop, route_name='dog', renderer='json')
        config.scan('model')
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()

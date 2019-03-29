from app.models import MHeroes
from flask import g

g.heroes_by_actor = None
def get_hero_by_actor(actor):
    if g.heroes_by_actor is None:
        g.heroes_by_actor = {}
        m_heroes = MHeroes.query.all()
        for m_hero in m_heroes:
            g.heroes_by_actor[m_hero.actor] = m_hero

    if actor in g.heroes_by_actor:
        return g.heroes_by_actor[actor]

    return None

def get_hero_id_by_actor(actor):
    hero = get_hero_by_actor(actor)
    if hero is not None:
        return hero.id

    return None
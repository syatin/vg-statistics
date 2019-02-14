from app.database import db
from app.models import MItems
from flask import g

g.item_master = None
def get_build_type(items):
    """
    Detect build_type by items
    アイテムからビルドを判定する
    """
    if g.item_master is None:
        g.item_master = {}
        m_items = MItems.query.all()
        for m_item in m_items:
            g.item_master[m_item.name] = m_item

    wp_tier_count = 0
    cp_tier_count = 0
    utility_tier_count = 0
    for item in items:
        if item in g.item_master:
            m_item = g.item_master[item]
            if m_item.build_type is None:
                continue
            elif m_item.build_type == 'wp':
                wp_tier_count += m_item.tier
            elif m_item.build_type == 'cp':
                cp_tier_count += m_item.tier
            elif m_item.build_type == 'support':
                utility_tier_count += m_item.tier
        else:
            m_item = MItems(name=item, item_id=item, type='other', tier=0)
            db.session.add(m_item)
            db.session.flush()
            g.item_master[item] = m_item

    max_tier = max(wp_tier_count, cp_tier_count, utility_tier_count)
    if max_tier != 0:
        if max_tier == wp_tier_count and max_tier == cp_tier_count:
            return 'HYBRID'
        elif max_tier == wp_tier_count:
            if cp_tier_count >= 3:
                return 'HYBRID'
            else:
                return 'WP'
        elif max_tier == cp_tier_count:
            if wp_tier_count >= 3:
                return 'HYBRID'
            else:
                return 'CP'
        elif max_tier == utility_tier_count:
            return 'UTILITY'

    return None

g.tier3_items = None
def get_tier3_items():
    if g.tier3_items is None:
        g.tier3_items = []
        m_items = MItems.query.filter_by(tier=3).all()
        for m_item in m_items:
            g.tier3_items.append(m_item.name)

    return g.tier3_items
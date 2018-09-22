
from app.models import MItems
from flask import g

g.item_master = None
def get_build_type(items):
    """
    アイテムからビルドを分析して返す
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
        m_item = g.item_master[item]
        if m_item is not None:
            if m_item.build_type is None:
                continue
            elif m_item.build_type == 'wp':
                wp_tier_count += m_item.tier
            elif m_item.build_type == 'cp':
                cp_tier_count += m_item.tier
            elif m_item.build_type == 'support':
                utility_tier_count += m_item.tier

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
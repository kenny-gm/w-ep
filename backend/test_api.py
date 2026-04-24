import sys
sys.path.insert(0, '/app')
from app.services.wb_api import WBApiClient
from app.database import engine
from sqlalchemy import text
import logging
logging.disable(logging.CRITICAL)

with engine.connect() as conn:
    shop = conn.execute(text('SELECT api_token FROM shops WHERE id = 1')).fetchone()
    api_token = shop[0]

client = WBApiClient(api_token)
adverts = client.get_adverts()
print(f'Found {len(adverts)} adverts')

ad_ids = [adv.get('id') for adv in adverts[:10] if adv.get('id')]
stats = client.get_ad_stats(ids=ad_ids, date_from='2026-04-16', date_to='2026-04-16')
print(f'Got {len(stats)} stat records')

target_nm_id = '547749797'
for stat in stats:
    advert_id = stat.get('advertId')
    days = stat.get('days', [])
    for day in days:
        date = day.get('date')
        apps = day.get('apps', [])
        for app in apps:
            nms = app.get('nms', [])
            for nm in nms:
                nm_id = str(nm.get('nmId', ''))
                if nm_id == target_nm_id:
                    nm_sum = nm.get('sum', 0)
                    print(f'Found nmId={nm_id} in advert_id={advert_id}, sum={nm_sum}')

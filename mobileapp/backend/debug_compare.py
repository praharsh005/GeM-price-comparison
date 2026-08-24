from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Product
from sqlalchemy import select

client = TestClient(app)
db = SessionLocal()
pid = db.scalar(select(Product.id).where(Product.name.ilike('%HP 15s%')))
print('pid:', pid)
r = client.get(f'/products/{pid}/compare')
body = r.json()
print('best_marketplace:', body.get('best_marketplace'))
print('best_price:', body.get('best_price'))
for l in body['listings']:
    print('  {}: {} (cheapest: {})'.format(l['marketplace_name'], l['price'], l['is_cheapest']))
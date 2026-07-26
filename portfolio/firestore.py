from decimal import Decimal

from django.utils import timezone

from finance.firebase import get_firestore_client

from .dataclasses import Holding, Portfolio

PORTFOLIOS_COLLECTION = "portfolios"
HOLDINGS_SUBCOLLECTION = "holdings"


def _portfolio_ref(uid):
    return get_firestore_client().collection(PORTFOLIOS_COLLECTION).document(uid)


def _holdings_collection(uid):
    return _portfolio_ref(uid).collection(HOLDINGS_SUBCOLLECTION)


def _holding_from_doc(doc):
    data = doc.to_dict()
    return Holding(
        id=doc.id,
        symbol=data.get("symbol", ""),
        name=data.get("name", ""),
        asset_type=data.get("asset_type", "STOCK"),
        quantity=Decimal(str(data.get("quantity", "0"))),
        cost_basis_per_unit=Decimal(str(data.get("cost_basis_per_unit", "0"))),
        current_price=Decimal(str(data.get("current_price", "0"))),
    )


def list_holdings(uid):
    docs = _holdings_collection(uid).order_by("symbol").stream()
    return [_holding_from_doc(doc) for doc in docs]


def get_or_create_portfolio(uid, name="My Portfolio"):
    ref = _portfolio_ref(uid)
    snapshot = ref.get()
    if snapshot.exists:
        data = snapshot.to_dict()
    else:
        data = {"name": name, "created_at": timezone.now().isoformat()}
        ref.set(data)
    return Portfolio(uid=uid, name=data.get("name", name), holdings=list_holdings(uid))


def get_holding(uid, holding_id):
    doc = _holdings_collection(uid).document(holding_id).get()
    if not doc.exists:
        return None
    return _holding_from_doc(doc)


def _serialize(data):
    return {
        "symbol": data["symbol"],
        "name": data.get("name", ""),
        "asset_type": data["asset_type"],
        "quantity": str(data["quantity"]),
        "cost_basis_per_unit": str(data["cost_basis_per_unit"]),
        "current_price": str(data["current_price"]),
    }


def add_holding(uid, data):
    ref = _holdings_collection(uid).document()
    ref.set(_serialize(data))
    return get_holding(uid, ref.id)


def update_holding(uid, holding_id, data):
    _holdings_collection(uid).document(holding_id).set(_serialize(data), merge=True)
    return get_holding(uid, holding_id)


def delete_holding(uid, holding_id):
    _holdings_collection(uid).document(holding_id).delete()

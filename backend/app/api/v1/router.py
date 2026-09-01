from fastapi import APIRouter

from app.api.v1.endpoints import assistant, analytics, auth, beneficiaries, bi, blockchain, catalogs, forecasting, funding_sources, remittances, risk, system, tracking, transactions, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(catalogs.router, prefix="/catalogs", tags=["catalogs"])
api_router.include_router(beneficiaries.router, prefix="/beneficiaries", tags=["beneficiaries"])
api_router.include_router(funding_sources.router, prefix="/funding-sources", tags=["funding-sources"])
api_router.include_router(remittances.router, prefix="/remittances", tags=["remittances"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(tracking.router, prefix="/tracking", tags=["tracking"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(bi.router, prefix="/bi", tags=["business-intelligence"])
api_router.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(forecasting.router, prefix="/forecasting", tags=["forecasting"])
api_router.include_router(system.router, prefix="/system", tags=["system"])

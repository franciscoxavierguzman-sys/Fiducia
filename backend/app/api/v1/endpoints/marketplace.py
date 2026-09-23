from datetime import UTC, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.marketplace import MarketplaceOrder, MarketplaceOrderItem, MarketplaceProduct
from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.transactions import link_received_transactions_by_email
from app.schemas.marketplace import (
    MarketplaceOrderCreate,
    MarketplaceOrderRead,
    MarketplaceProductRead,
    MarketplaceRemittanceBalanceRead,
)
from app.services.audit import log_audit_event

router = APIRouter()


@router.get("/products", response_model=list[MarketplaceProductRead])
def list_products(db: Session = Depends(get_db)) -> list[MarketplaceProduct]:
    return list(
        db.scalars(
            select(MarketplaceProduct)
            .where(MarketplaceProduct.is_active.is_(True), MarketplaceProduct.stock > 0)
            .order_by(MarketplaceProduct.category, MarketplaceProduct.name)
        )
    )


@router.get("/balances", response_model=list[MarketplaceRemittanceBalanceRead])
def list_remittance_balances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MarketplaceRemittanceBalanceRead]:
    link_received_transactions_by_email(db, current_user.id, current_user.email)
    db.commit()
    balances = []
    for transaction in list_completed_received_remittances(db, current_user.id):
        spent_amount = get_spent_amount(db, transaction.id)
        original_amount = Decimal(transaction.destination_amount)
        available_amount = max(Decimal("0.00"), original_amount - spent_amount)
        balances.append(
            MarketplaceRemittanceBalanceRead(
                transaction_id=transaction.id,
                remittance_number=transaction.transaction_id or f"FID-{transaction.id}",
                currency=transaction.destination_currency,
                original_amount=original_amount,
                spent_amount=spent_amount,
                available_amount=available_amount,
                completed_at=transaction.updated_at,
            )
        )
    return balances


@router.get("/orders", response_model=list[MarketplaceOrderRead])
def list_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MarketplaceOrder]:
    return list(
        db.scalars(
            select(MarketplaceOrder)
            .options(joinedload(MarketplaceOrder.items).joinedload(MarketplaceOrderItem.product))
            .where(MarketplaceOrder.buyer_id == current_user.id)
            .order_by(MarketplaceOrder.created_at.desc())
        )
        .unique()
    )


@router.post("/orders", response_model=MarketplaceOrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: MarketplaceOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketplaceOrder:
    link_received_transactions_by_email(db, current_user.id, current_user.email)
    transaction = db.scalar(
        select(Transaction).where(
            Transaction.id == payload.remittance_transaction_id,
            Transaction.beneficiary_user_id == current_user.id,
        )
    )
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "REMITTANCE_NOT_FOUND", "message": "Remesa recibida no encontrada"},
        )
    if transaction.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "REMITTANCE_NOT_COMPLETED", "message": "La remesa debe estar recibida para comprar"},
        )

    products = load_products_for_order(db, [item.product_id for item in payload.items])
    subtotal = Decimal("0.00")
    currency = transaction.destination_currency
    order_items: list[MarketplaceOrderItem] = []
    quantity_by_product: dict[int, int] = {}
    for item in payload.items:
        quantity_by_product[item.product_id] = quantity_by_product.get(item.product_id, 0) + item.quantity

    for product_id, quantity in quantity_by_product.items():
        product = products.get(product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PRODUCT_NOT_FOUND", "message": "Producto no encontrado"},
            )
        if product.currency != currency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "CURRENCY_MISMATCH", "message": "La moneda del producto no coincide con la remesa"},
            )
        if product.stock < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INSUFFICIENT_STOCK", "message": "Inventario insuficiente"},
            )
        line_total = Decimal(product.price_amount) * Decimal(quantity)
        subtotal += line_total
        order_items.append(
            MarketplaceOrderItem(
                product_id=product.id,
                quantity=quantity,
                unit_price_amount=product.price_amount,
                total_amount=line_total,
            )
        )

    available_amount = Decimal(transaction.destination_amount) - get_spent_amount(db, transaction.id)
    if subtotal > available_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INSUFFICIENT_REMITTANCE_BALANCE", "message": "Saldo de remesa insuficiente"},
        )

    order = MarketplaceOrder(
        buyer_id=current_user.id,
        remittance_transaction_id=transaction.id,
        status="PAID",
        subtotal_amount=subtotal,
        total_amount=subtotal,
        currency=currency,
        created_at=datetime.now(UTC),
    )
    db.add(order)
    db.flush()
    order.order_number = f"MKT-{datetime.now(UTC).year}-{order.id:06d}"
    for item in order_items:
        item.order_id = order.id
        db.add(item)
        products[item.product_id].stock -= item.quantity

    log_audit_event(
        db,
        user_id=current_user.id,
        action="MARKETPLACE_ORDER_PAID",
        entity="marketplace_order",
        entity_id=order.order_number,
        metadata={
            "remittance_transaction_id": transaction.id,
            "total_amount": str(order.total_amount),
            "currency": order.currency,
        },
    )
    db.commit()
    return db.scalar(
        select(MarketplaceOrder)
        .options(joinedload(MarketplaceOrder.items).joinedload(MarketplaceOrderItem.product))
        .where(MarketplaceOrder.id == order.id)
    )


def list_completed_received_remittances(db: Session, user_id: int) -> list[Transaction]:
    return list(
        db.scalars(
            select(Transaction)
            .where(Transaction.beneficiary_user_id == user_id, Transaction.status == "COMPLETED")
            .order_by(Transaction.updated_at.desc())
        )
    )


def get_spent_amount(db: Session, transaction_id: int) -> Decimal:
    value = db.scalar(
        select(func.coalesce(func.sum(MarketplaceOrder.total_amount), 0)).where(
            MarketplaceOrder.remittance_transaction_id == transaction_id,
            MarketplaceOrder.status == "PAID",
        )
    )
    return Decimal(value or 0).quantize(Decimal("0.01"))


def load_products_for_order(db: Session, product_ids: list[int]) -> dict[int, MarketplaceProduct]:
    return {
        product.id: product
        for product in db.scalars(
            select(MarketplaceProduct).where(
                MarketplaceProduct.id.in_(set(product_ids)),
                MarketplaceProduct.is_active.is_(True),
            )
        )
    }

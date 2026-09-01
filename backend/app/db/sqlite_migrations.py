from sqlalchemy import inspect, text

from app.db.session import engine


def ensure_sqlite_schema_compatibility() -> None:
    if not engine.url.drivername.startswith("sqlite"):
        return

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    with engine.begin() as connection:
        if "users" in table_names:
            columns = {column["name"] for column in inspector.get_columns("users")}
            if "document_type" not in columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN document_type VARCHAR(30)"))

        if "countries" in table_names:
            columns = {column["name"] for column in inspector.get_columns("countries")}
            if "currency_name" not in columns:
                connection.execute(text("ALTER TABLE countries ADD COLUMN currency_name VARCHAR(80)"))
            if "currency_symbol" not in columns:
                connection.execute(text("ALTER TABLE countries ADD COLUMN currency_symbol VARCHAR(8)"))

        if "beneficiaries" in table_names:
            columns = {column["name"] for column in inspector.get_columns("beneficiaries")}
            if "beneficiary_user_id" not in columns:
                connection.execute(text("ALTER TABLE beneficiaries ADD COLUMN beneficiary_user_id INTEGER"))
            if "email" not in columns:
                connection.execute(text("ALTER TABLE beneficiaries ADD COLUMN email VARCHAR(255)"))
            if "phone" not in columns:
                connection.execute(text("ALTER TABLE beneficiaries ADD COLUMN phone VARCHAR(30)"))
            if "relationship_id" not in columns:
                connection.execute(text("ALTER TABLE beneficiaries ADD COLUMN relationship_id INTEGER"))
            if "relationship_other" not in columns:
                connection.execute(text("ALTER TABLE beneficiaries ADD COLUMN relationship_other VARCHAR(120)"))
            if "country" not in columns:
                connection.execute(text("ALTER TABLE beneficiaries ADD COLUMN country VARCHAR(100) NOT NULL DEFAULT 'Guatemala'"))
            if "currency" not in columns:
                connection.execute(text("ALTER TABLE beneficiaries ADD COLUMN currency VARCHAR(3) NOT NULL DEFAULT 'GTQ'"))
            if "city" not in columns:
                connection.execute(text("ALTER TABLE beneficiaries ADD COLUMN city VARCHAR(120)"))

        if "funding_sources" in table_names:
            columns = {column["name"] for column in inspector.get_columns("funding_sources")}
            if "account_type" not in columns:
                connection.execute(text("ALTER TABLE funding_sources ADD COLUMN account_type VARCHAR(40)"))
            if "card_expiry" not in columns:
                connection.execute(text("ALTER TABLE funding_sources ADD COLUMN card_expiry VARCHAR(5)"))

        if "transactions" in table_names:
            columns = {column["name"] for column in inspector.get_columns("transactions")}
            if "remittance_uuid" not in columns:
                connection.execute(text("ALTER TABLE transactions ADD COLUMN remittance_uuid VARCHAR(36)"))
            if "funding_source_id" not in columns:
                connection.execute(text("ALTER TABLE transactions ADD COLUMN funding_source_id INTEGER"))
            if "source_amount" not in columns:
                connection.execute(text("ALTER TABLE transactions ADD COLUMN source_amount NUMERIC(12, 2)"))
                connection.execute(text("UPDATE transactions SET source_amount = amount WHERE source_amount IS NULL"))
            if "source_currency" not in columns:
                connection.execute(text("ALTER TABLE transactions ADD COLUMN source_currency VARCHAR(3)"))
                connection.execute(text("UPDATE transactions SET source_currency = currency WHERE source_currency IS NULL"))
            if "destination_currency" not in columns:
                connection.execute(text("ALTER TABLE transactions ADD COLUMN destination_currency VARCHAR(3)"))
                connection.execute(text("UPDATE transactions SET destination_currency = 'GTQ' WHERE destination_currency IS NULL"))
            connection.execute(text("UPDATE transactions SET destination_currency = 'GTQ' WHERE destination_country = 'Guatemala' AND destination_currency IS NULL"))
            if "beneficiary_user_id" not in columns:
                connection.execute(text("ALTER TABLE transactions ADD COLUMN beneficiary_user_id INTEGER"))
            if "debit_amount" not in columns:
                connection.execute(text("ALTER TABLE transactions ADD COLUMN debit_amount NUMERIC(14, 2)"))
                connection.execute(text("UPDATE transactions SET debit_amount = total_amount WHERE debit_amount IS NULL"))
            if "debit_currency" not in columns:
                connection.execute(text("ALTER TABLE transactions ADD COLUMN debit_currency VARCHAR(3)"))
                connection.execute(text("UPDATE transactions SET debit_currency = currency WHERE debit_currency IS NULL"))

        if "risk_assessments" in table_names:
            columns = {column["name"] for column in inspector.get_columns("risk_assessments")}
            if "assessment_sequence" not in columns:
                connection.execute(text("ALTER TABLE risk_assessments ADD COLUMN assessment_sequence INTEGER NOT NULL DEFAULT 1"))
            if "weights_json" not in columns:
                connection.execute(text("ALTER TABLE risk_assessments ADD COLUMN weights_json JSON"))
            if "risk_band_thresholds_json" not in columns:
                connection.execute(text("ALTER TABLE risk_assessments ADD COLUMN risk_band_thresholds_json JSON"))
            if "signal_status_json" not in columns:
                connection.execute(text("ALTER TABLE risk_assessments ADD COLUMN signal_status_json JSON"))

        if "assistant_conversations" not in table_names:
            connection.execute(
                text(
                    """
                    CREATE TABLE assistant_conversations (
                        id INTEGER NOT NULL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        title VARCHAR(160) NOT NULL,
                        is_active BOOLEAN NOT NULL DEFAULT 1,
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users (id)
                    )
                    """
                )
            )
            connection.execute(text("CREATE INDEX ix_assistant_conversations_id ON assistant_conversations (id)"))
            connection.execute(text("CREATE INDEX ix_assistant_conversations_user_id ON assistant_conversations (user_id)"))

        if "assistant_messages" not in table_names:
            connection.execute(
                text(
                    """
                    CREATE TABLE assistant_messages (
                        id INTEGER NOT NULL PRIMARY KEY,
                        conversation_id INTEGER NOT NULL,
                        role VARCHAR(20) NOT NULL,
                        content TEXT NOT NULL,
                        intent VARCHAR(80),
                        provider VARCHAR(80),
                        tools_used_json JSON,
                        sources_json JSON,
                        safety_events_json JSON,
                        metadata_json JSON,
                        created_at DATETIME NOT NULL,
                        FOREIGN KEY(conversation_id) REFERENCES assistant_conversations (id)
                    )
                    """
                )
            )
            connection.execute(text("CREATE INDEX ix_assistant_messages_id ON assistant_messages (id)"))
            connection.execute(text("CREATE INDEX ix_assistant_messages_conversation_id ON assistant_messages (conversation_id)"))

import os
from dotenv import load_dotenv

# Load env before importing backend modules to ensure APP_ENCRYPTION_KEY is set
load_dotenv()

from backend.database import SessionLocal
from backend.models import UserPlugin
from backend.brokers.mstock import MStockConnector
from backend.crypto_utils import decrypt_credentials

def run_test():
    db = SessionLocal()
    try:
        # Find the first mstock plugin
        plugin = db.query(UserPlugin).filter(UserPlugin.plugin_name == "mstock").first()
        if not plugin:
            print("No mStock plugin found in database.")
            return

        print(f"Found plugin: {plugin.label} (ID: {plugin.id})")
        
        # Decrypt credentials
        creds = decrypt_credentials(plugin.credentials_encrypted)
        
        # Mask credentials for logging
        masked_creds = {k: "********" for k in creds.keys()}
        print(f"Decrypted credentials successfully: {masked_creds.keys()}")
        
        # Initialize connector
        connector = MStockConnector(creds)
        
        print("Ensuring session (Calling verifytotp)...")
        connector.ensure_session()
        print(f"Session established! Access Token starts with: {connector._access_token[:10]}...")
        
        print("Fetching holdings...")
        holdings = connector.fetch_holdings()
        print(f"Successfully fetched {len(holdings)} holdings!")
        
        for h in holdings[:5]:
            print(f"- {h.symbol} ({h.exchange}): {h.quantity} @ {h.avg_buy_price}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_test()

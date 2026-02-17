import httpx
from datetime import datetime
import os
from .database import SessionLocal
from .models import CurrencyRate

class CurrencyService:
    def __init__(self):
        self.api_key = os.getenv("EXCHANGERATE_API_KEY")
        self.base_url = "https://v6.exchangerate-api.com/v6"
        
    async def get_latest_rate(self, from_curr: str, to_curr: str) -> float:
        db = SessionLocal()
        try:
            # Check DB cache first (valid for 24h)
            rate_record = db.query(CurrencyRate).filter(
                CurrencyRate.from_currency == from_curr,
                CurrencyRate.to_currency == to_curr
            ).first()
            
            if rate_record and (datetime.now() - rate_record.updated_at).hours < 24:
                return rate_record.rate
            
            # Fetch from API
            if not self.api_key:
                return 1.0 # Fallback for dev
                
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/{self.api_key}/pair/{from_curr}/{to_curr}"
                response = await client.get(url)
                data = response.json()
                
                if data["result"] == "success":
                    rate = data["conversion_rate"]
                    
                    # Update DB
                    if rate_record:
                        rate_record.rate = rate
                        rate_record.updated_at = func.now()
                    else:
                        new_rate = CurrencyRate(from_currency=from_curr, to_currency=to_curr, rate=rate)
                        db.add(new_rate)
                    db.commit()
                    return rate
                    
            return 1.0 # Final fallback
        finally:
            db.close()

    def format_currency(self, amount: float, currency: str, use_lakhs_crores: bool = True) -> str:
        if currency == "MYR":
            return f"RM {amount:,.2f}"
        elif currency == "INR" and use_lakhs_crores:
            if amount >= 10000000: # 1 Crore
                return f"₹{amount/10000000:.2f} Cr"
            elif amount >= 100000: # 1 Lakh
                return f"₹{amount/100000:.2f} L"
            return f"₹{amount:,.2f}"
        elif currency == "USD":
            return f"${amount:,.2f}"
        return f"{currency} {amount:,.2f}"

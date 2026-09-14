# mStock API Reference

## Useful Links
- **Introduction**: https://tradingapi.mstock.com/docs/v1/Introduction/
- **Type A APIs (User/Login)**: https://tradingapi.mstock.com/docs/v1/typeA/User/
- **Type B APIs (Portfolio/Holdings)**: https://tradingapi.mstock.com/docs/v1/typeB/User/
- **Key Generation**: https://www.mstock.com/trading-api

## Key Integration Details

### Authentication Flow (Type A)
1. **Endpoint**: `POST https://api.mstock.trade/openapi/typea/session/verifytotp`
2. **Headers**:
   - `X-Mirae-Version: 1`
   - `Content-Type: application/x-www-form-urlencoded`
3. **Payload (form-data)**:
   - `api_key`: (From Developer Portal)
   - `totp`: (6-digit TOTP code generated using Base32 Secret)
4. **Response**: Returns the access token (could be under `access_token`, `enctoken`, or `jwtToken` fields within `data`).

### Fetching Holdings (Type B)
1. **Endpoint**: `GET https://api.mstock.trade/openapi/typeb/portfolio/holdings`
2. **Headers**:
   - `X-Mirae-Version: 1`
   - `Authorization: Bearer <jwtToken>`
   - `X-PrivateKey: <api_key>`
3. **Response format**:
   ```json
   {
       "status": "true",
       "message": "SUCCESS",
       "errorcode": null,
       "data": [
           {
               "tradingsymbol": "BANK OF MAHARASHTRA",
               "quantity": 10,
               "averageprice": 30,
               "ltp": 84.7,
               "profitandloss": 0
           }
       ]
   }
   ```
   *Note: Only process holdings where `quantity > 0`.*

### Important Quirks
- **Tokens expire daily**: Tokens are valid until 12:00 AM of the generated day.
- **Header discrepancies**: Type A endpoints (like Fund Summary) expect `Authorization: token <api_key>:<token>` whereas Type B endpoints (like Portfolio) expect `Authorization: Bearer <jwtToken>` and `X-PrivateKey: <api_key>`.
- **502 Bad Gateway on TOTP**: Although TOTP accounts do not require an OTP from the `/login` endpoint, hitting `/verifytotp` completely cold can often result in a `502 Bad Gateway`. To bypass this, call `/connect/login` with your username and password first to initialize session state on their end, and then call `/verifytotp` on the same connection.

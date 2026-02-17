#### 2. **ARCHITECTURE.md** - The "How"
**Purpose**: Technical decisions and system design

**Should contain**:
```markdown
# System Architecture

## Tech Stack
- Backend: FastAPI (Python 3.11+)
- Database: PostgreSQL 15
- Cache: Redis
- Frontend: React 18 + TypeScript + Tailwind
- Deployment: HOSTINGER or Any other VPS
-Lean & Modern

## Database Schema
[Link to schema diagrams you already have]

## API Integrations
- Binance API
- LUNO API
- Zerodha Kite API
- IBKR Client Portal API
- ExchangeRate-API (currency conversion)

## Plugin System
[Description of how custom plugins work]

## Security
- API keys encrypted at rest (Fernet)
- Read-only broker permissions
- JWT authentication
- HTTPS only
```
# Project Asta: Security Best Practices

## 1. API Key Management
- **Never Hardcode Secrets**: All API keys (MetaApi, Gemini, Database passwords) must be stored in environment variables or a secure secret manager (e.g., AWS Secrets Manager, HashiCorp Vault).
- **Encryption at Rest**: Sensitive data in the database (if any) should be encrypted.
- **Environment Isolation**: Use separate keys for Development, Staging, and Production environments.

## 2. Infrastructure Security
- **Nginx Reverse Proxy**: Always use Nginx as a reverse proxy to handle SSL termination (HTTPS) and hide the application server from direct internet exposure.
- **SSL/TLS**: Use modern TLS versions (1.2+) and strong cipher suites.
- **VPC & Firewalls**: Run the database and Redis in a private subnet, accessible only by the backend service.

## 3. Application Security
- **Authentication**: All dashboard endpoints must be protected by JWT-based authentication.
- **Rate Limiting**: Implement rate limiting on both API endpoints and trade execution to prevent brute-force attacks or accidental rapid-fire orders (fat-finger protection).
- **Audit Trails**: Log every critical decision, trade execution, and risk rejection for post-incident analysis.
- **Input Validation**: Use Pydantic for strict schema validation of all incoming data.

## 4. Operational Security
- **Least Privilege**: Grant the bot only the necessary permissions on the broker account (e.g., restricted withdrawal rights).
- **Dependency Scanning**: Regularly run `safety` or `snyk` to check for vulnerabilities in Python packages.
- **Structured Logging**: Use JSON logging to facilitate centralized monitoring and anomaly detection.

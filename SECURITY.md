# Security

- Never commit `.env`, marketplace tokens, database passwords, JWT secrets, or AI provider keys.
- Copy `.env.example` to `.env` locally and replace all development secrets before production deployment.
- If `.env` was ever committed, rotate `SECRET_KEY`, `POSTGRES_PASSWORD`, Wildberries tokens, and any AI provider keys, then remove the file from Git history before making the repository public.
- Keep the repository private until a secret scan reports no credentials.

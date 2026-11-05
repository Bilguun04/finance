# Finance Tracker (SvelteKit)

SvelteKit port of the Django app in the repository root: portfolios and trading, a bankroll session log,
friends with shared portfolio allocations, and a live market landing page.

Stack: SvelteKit 3 + Svelte 5, Drizzle ORM on PostgreSQL, better-auth (username + password),
Tailwind CSS 4, deployed to Cloudflare Workers.

## Setup

```sh
npm install
cp .env.example .env        # then fill in BETTER_AUTH_SECRET and, optionally, FINNHUB_API_KEY
npm run db:start            # Postgres in Docker (compose.yaml)
npm run db:migrate          # apply drizzle/ migrations
npm run dev
```

After changing `src/lib/server/db/schema.ts`, run `npm run db:generate` and commit the new migration.

## Where things live

| Django app  | SvelteKit                                                                       |
| ----------- | ------------------------------------------------------------------------------- |
| `core`      | `src/routes/+page.*`, `src/routes/api/market/*`, `src/lib/server/market.ts`     |
| `account`   | `src/routes/account/*`, `src/lib/server/auth.ts`, `src/lib/server/passwords.ts` |
| `portfolio` | `src/routes/portfolio/*`, `src/lib/server/portfolio*.ts`                        |
| `bankroll`  | `src/routes/bankroll/*`, `src/lib/server/bankroll.ts`                           |
| `social`    | `src/routes/social/*`, `src/lib/server/social.ts`                               |
| models      | `src/lib/server/db/schema.ts` (+ `auth.schema.ts` for better-auth's tables)     |

## Notes

- Password reset emails are printed to the server console (like Django's console email backend).
  Replace `sendResetPassword` in `src/lib/server/auth.ts` with a real email provider for production.
- On Cloudflare Workers each request opens its own database connection (`src/lib/server/db/index.ts`).
  For production, put the database behind Cloudflare Hyperdrive to keep connections pooled.
- Tests: `npm test` runs unit tests for the money maths, market hours, form validation and formatting.

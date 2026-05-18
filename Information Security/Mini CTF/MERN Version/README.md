# Mini CTF - MERN Conversion

This folder is a MERN rewrite of the Flask Mini CTF project.

## Stack
- Backend: Node.js, Express, MongoDB (Mongoose)
- Frontend: React (Vite), React Router, Axios
- Auth: JWT in HttpOnly cookie

## Features Ported
- Auth (register, login, logout, current user)
- Role-based access (player/admin)
- Player dashboard, challenge listing, flag submissions, hints, scoreboard
- Admin dashboard, users, challenges, submissions, logs APIs
- Challenge-specific routes for:
  - sqli
  - idor
  - xss
  - bac
  - crypto
  - hash
  - rsa
  - bruteforce
  - diffie
  - vigenere

## Setup
### 1) Server
```bash
cd server
cp .env.example .env
npm install
npm run seed
npm run dev
```

### 2) Client
```bash
cd client
cp .env.example .env
npm install
npm run dev
```

Client runs on http://localhost:5173 and expects API at http://localhost:5000/api.

## Default Accounts
- admin / Admin@1337
- player1 / player123

## Notes
- This preserves intentional CTF vulnerabilities by design for educational use.
- BAC challenge intentionally exposes `GET /api/challenges/bac/secret-panel` with login-only protection.

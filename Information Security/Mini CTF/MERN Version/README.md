# CTF Platform - MERN Stack

A complete Capture The Flag (CTF) platform built with MERN (MongoDB, Express, React, Node.js). Features 10 different security challenges, user dashboards, admin panels, and a comprehensive points/leaderboard system.

## Project Structure

```
ctf-platform/
├── backend/                 # Express.js + MongoDB
│   ├── models/             # Mongoose schemas
│   ├── routes/             # API routes
│   ├── controllers/        # Business logic
│   ├── middleware/         # Auth middleware
│   ├── config/             # Database config
│   ├── server.js           # Main server file
│   ├── .env                # Environment variables
│   └── package.json
│
└── frontend/               # React + Vite
    ├── src/
    │   ├── pages/          # Page components
    │   ├── components/     # Reusable components
    │   ├── api/            # API client
    │   ├── App.jsx         # Main app component
    │   └── index.css       # Global styles
    ├── vite.config.js
    └── package.json
```

## 10 Challenges

1. **SQL Injection** - Exploit vulnerable login form (100 pts)
2. **IDOR (Insecure Direct Object Reference)** - Access unauthorized user profiles (100 pts)
3. **Stored XSS** - Inject and execute malicious scripts (150 pts)
4. **Broken Access Control (BAC)** - Bypass admin panel authentication (150 pts)
5. **Hash Cracking** - Crack MD5 password hash (75 pts)
6. **RSA Decryption** - Decrypt RSA message with small primes (200 pts)
7. **Brute Force** - Guess admin password from wordlist (100 pts)
8. **Diffie-Hellman** - Compute shared secret from DH parameters (200 pts)
9. **Vigenere Cipher** - Decrypt polyalphabetic cipher (150 pts)
10. **ROT13 Decryption** - Decode ROT13 encrypted message (50 pts)

**Total: 1,175 points**

## Setup Instructions

### Prerequisites
- Node.js 14+
- MongoDB (local or Atlas)
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file with your configuration:
```env
MONGODB_URI=mongodb://localhost:27017/ctf_platform
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin@1337
SESSION_SECRET=ctf_secret_key_2024_secure
PORT=5000
NODE_ENV=development
```

4. Start the backend server:
```bash
npm start
# or for development with auto-reload:
npm run dev
```

Backend runs on: `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

Frontend runs on: `http://localhost:5173`

### Default Admin Credentials

- **Username:** admin
- **Password:** Admin@1337

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user

### Challenges
- `GET /api/challenges` - Get all challenges
- `GET /api/challenges/:id` - Get single challenge
- `POST /api/challenges/submit` - Submit flag
- `GET /api/challenges/stats` - Get challenge statistics
- `GET /api/challenges/progress` - Get user progress

### Admin
- `GET /api/admin/check` - Check if user is admin
- `GET /api/admin/stats` - Get admin dashboard statistics
- `GET /api/admin/users` - Get all users
- `GET /api/admin/submissions` - Get all submissions
- `GET /api/admin/challenge/:id` - Get challenge details with analytics

## Features

### User Dashboard
- View all 10 challenges with difficulty levels and points
- Track personal progress with visual progress bar
- See completed challenges and earned points
- Quick access to each challenge

### Challenge Pages
- Detailed challenge descriptions
- Interactive challenge interface (varies by challenge type)
- Flag submission form with real-time feedback
- Point rewards on successful flag submission

### Admin Dashboard
- Overview statistics (users, challenges, submissions)
- Leaderboard showing top 10 users
- User management table
- Submission history with correct/incorrect tracking
- Challenge analytics

### Authentication
- User registration with validation
- Session-based authentication (no JWT for simplicity)
- Password hashing with bcryptjs
- Admin role management

### Leaderboard & Scoring
- Automatic point calculation on flag submission
- First blood tracking (first solver of each challenge)
- User ranking system
- Challenge completion statistics

## Database Schema

### User Collection
```javascript
{
  username: String,
  password: String (hashed),
  email: String,
  isAdmin: Boolean,
  totalPoints: Number,
  solvedChallenges: [{
    challengeId: String,
    solvedAt: Date,
    points: Number
  }],
  createdAt: Date
}
```

### Challenge Collection
```javascript
{
  id: String,
  name: String,
  description: String,
  category: String,
  difficulty: String (Easy/Medium/Hard),
  points: Number,
  flag: String,
  firstBlood: {
    userId: String,
    username: String,
    solvedAt: Date
  },
  solveCount: Number,
  submissions: Number
}
```

### Submission Collection
```javascript
{
  userId: String,
  username: String,
  challengeId: String,
  challengeName: String,
  flag: String,
  isCorrect: Boolean,
  points: Number,
  submittedAt: Date
}
```

## Design Features

- **Solid Color Scheme:** Blue primary (#2563eb), gray neutrals, green success, red error
- **Clean Typography:** System fonts with max 2 font families
- **Responsive Layout:** Mobile-first design with flexbox layouts
- **No Animations:** Smooth transitions only, no decorative animations
- **Accessibility:** Semantic HTML, proper contrast ratios

## Security Notes

This is an educational CTF platform. Some features intentionally demonstrate vulnerabilities:
- SQL Injection challenges show vulnerable patterns
- XSS challenges demonstrate injection techniques
- IDOR challenges show improper access control
- BAC challenges demonstrate broken authentication

These are **not** recommended for production systems.

## Future Enhancements

- Team-based challenges
- Real-time leaderboard updates with WebSockets
- Challenge categories and filtering
- User profile pages
- Challenge discussion/hints system
- Time-based scoring (bonus for fast solves)
- Difficulty-based point scaling
- User badges and achievements

## License

Educational use only.

## Support

For issues or questions, check the code comments or review the API documentation in this README.

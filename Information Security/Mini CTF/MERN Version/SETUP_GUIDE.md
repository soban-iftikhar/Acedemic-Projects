# MERN Version Setup Guide

## 📋 Prerequisites
- Node.js 16+ and npm
- MongoDB Atlas account (or local MongoDB)
- Git

## 🚀 Installation & Setup

### Part 1: Backend Setup

#### 1. Navigate to Backend Directory
```bash
cd "MERN Version/backend"
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Configure Environment Variables
The `.env` file is already configured with:
```env
MONGO_URI=mongodb+srv://soban:soban1234@tutorialcluster.p1kgwty.mongodb.net/?appName=TutorialCluster
PORT=5000
CLIENT_URL=http://localhost:3000
JWT_SECRET=your_jwt_secret_key_change_this_in_production
```

#### 4. Seed Database (Optional)
```bash
npm run seed
```

#### 5. Start Backend Server
```bash
npm run dev
# Backend runs on http://localhost:5000
```

### Part 2: Frontend Setup

#### 1. Open New Terminal & Navigate to Frontend
```bash
cd "MERN Version/frontend"
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Configure Environment Variables
The `.env` file is already configured with:
```env
VITE_API_URL=http://localhost:5000/api
```

#### 4. Start Frontend Development Server
```bash
npm run dev
# Frontend runs on http://localhost:5173
```

## 🎯 Available Scripts

### Backend
```bash
npm run dev     # Start with nodemon (auto-reload)
npm start       # Start production server
npm run seed    # Seed database with sample data
```

### Frontend
```bash
npm run dev      # Start Vite dev server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

## 📁 Project Structure

```
MERN Version/
├── backend/
│   ├── src/
│   │   ├── app.js
│   │   ├── config/
│   │   │   ├── db.js
│   │   │   └── constants.js
│   │   ├── routes/
│   │   │   ├── authRoutes.js
│   │   │   ├── challengeRoutes.js
│   │   │   ├── playerRoutes.js
│   │   │   └── adminRoutes.js
│   │   ├── models/
│   │   │   ├── User.js
│   │   │   ├── Challenge.js
│   │   │   ├── Submission.js
│   │   │   ├── ActivityLog.js
│   │   │   └── XssMessage.js
│   │   ├── middleware/
│   │   │   ├── auth.js
│   │   │   └── logActivity.js
│   │   └── scripts/
│   │       └── seed.js
│   ├── .env
│   ├── package.json
│   └── .gitignore
│
└── frontend/
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx
    │   ├── pages/
    │   ├── components/
    │   ├── context/
    │   └── lib/
    ├── public/
    ├── .env
    ├── vite.config.js
    ├── package.json
    └── .gitignore
```

## 🔐 Environment Configuration

### Backend (.env)
```env
MONGO_URI=mongodb+srv://soban:soban1234@tutorialcluster.p1kgwty.mongodb.net/?appName=TutorialCluster
PORT=5000
CLIENT_URL=http://localhost:3000
JWT_SECRET=your_jwt_secret_key_change_this_in_production
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000/api
```

## 📊 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React 18 + Vite |
| Backend | Express.js + Node.js |
| Database | MongoDB Atlas |
| Auth | JWT + httpOnly Cookies |
| HTTP | CORS enabled |

## 🎯 7 Security Challenges

1. **SQL Injection** (100 pts) - Easy
2. **IDOR** (100 pts) - Easy  
3. **XSS** (200 pts) - Medium
4. **Command Injection** (200 pts) - Medium
5. **File Upload** (300 pts) - Hard
6. **Broken Access Control** (100 pts) - Easy
7. **Cryptography** (300 pts) - Hard

**Total Points:** 1300

## 🧪 Testing the Setup

### 1. Verify Backend Connection
```bash
curl http://localhost:5000/api/health
```

### 2. Check Frontend loads
Visit: http://localhost:5173

## 🛠️ Troubleshooting

### MongoDB Connection Error
```
Error: getaddrinfo ENOTFOUND
```
- Verify MONGO_URI in .env is correct
- Check MongoDB Atlas IP whitelist
- Ensure credentials are correct

### Port Already in Use
```bash
# Check what's using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or change PORT in .env
PORT=5001
```

### CORS Errors
- Ensure CLIENT_URL in backend .env matches your frontend URL
- Check browser console for specific CORS errors

### Dependencies Not Installing
```bash
# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## 🚀 Deployment

### Production Build
```bash
# Build frontend
cd frontend
npm run build

# Deploy 'dist' folder to static hosting (Vercel, Netlify, etc.)

# Deploy backend to Node.js hosting (Railway, Heroku, etc.)
```

### Production Environment Variables
```env
MONGO_URI=<production-mongodb-uri>
PORT=3000
CLIENT_URL=<production-client-url>
JWT_SECRET=<generate-strong-secret>
NODE_ENV=production
```

## 📚 Learning Resources

- [Express.js Docs](https://expressjs.com/)
- [React Docs](https://react.dev/)
- [MongoDB Docs](https://www.mongodb.com/docs/)
- [Vite Docs](https://vitejs.dev/)
- [JWT Docs](https://jwt.io/)

## ⚠️ Security Notes

- ✅ Change JWT_SECRET in production
- ✅ Use HTTPS in production
- ✅ Implement rate limiting for login endpoints
- ✅ Add CSRF protection
- ✅ Validate all user inputs
- ✅ Use environment variables for secrets
- ✅ Keep dependencies updated

---
**Last Updated:** May 18, 2026

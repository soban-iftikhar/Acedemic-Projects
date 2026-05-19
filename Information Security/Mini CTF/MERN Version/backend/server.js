const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });
const express = require('express');
const mongoose = require('mongoose');
const session = require('express-session');
const MongoStore = require('connect-mongo');
const cors = require('cors');
const connectDB = require('./config/db');
const User = require('./models/User');
const Challenge = require('./models/Challenge');

// Middleware
const app = express();

// Database connection
connectDB();

// CORS
app.use(cors({
  origin: 'http://localhost:5173',
  credentials: true
}));

// Body parser
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Session configuration
const mongoUri = process.env.MONGODB_URI || process.env.MONGO_URI;
if (!mongoUri) {
  throw new Error('Missing MongoDB URI. Set MONGODB_URI or MONGO_URI in backend/.env');
}

app.use(session({
  secret: process.env.SESSION_SECRET || 'ctf_secret',
  resave: false,
  saveUninitialized: false,
  store: MongoStore.create({
    mongoUrl: mongoUri,
    touchAfter: 24 * 3600
  }),
  cookie: {
    secure: false,
    httpOnly: true,
    maxAge: 24 * 60 * 60 * 1000 // 24 hours
  }
}));

// Routes
app.use('/api/auth', require('./routes/auth'));
app.use('/api/challenges', require('./routes/challenges'));
app.use('/api/admin', require('./routes/admin'));

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK' });
});

// Initialize challenges on startup
const initializeChallenges = async () => {
  try {
    const challenges = [
        {
          id: 'sqli',
          slug: 'sqli',
          name: 'SQL Injection',
          description: 'Bypass the login form with SQL injection.',
          category: 'Web Security',
          difficulty: 'Easy',
          points: 100,
          flag: 'flag{sql_1nj3ct10n_byp4ss_m4st3r}'
        },
        {
          id: 'idor',
          slug: 'idor',
          name: 'Broken Access Control (IDOR)',
          description: 'Change the profile id in the URL.',
          category: 'Web Security',
          difficulty: 'Easy',
          points: 100,
          flag: 'flag{1d0r_pr0f1l3_3num3r4t10n}'
        },
        {
          id: 'xss',
          slug: 'xss',
          name: 'Stored XSS',
          description: 'Post script content and view the stored message.',
          category: 'Web Security',
          difficulty: 'Medium',
          points: 150,
          flag: 'flag{xss_scr1pt_1nj3ct3d_c00k13}'
        },
        {
          id: 'bac',
          slug: 'bac',
          name: 'Broken Access Control (Admin Panel)',
          description: 'An admin-only area exists, but visibility and authorization are not always the same thing.',
          category: 'Web Security',
          difficulty: 'Medium',
          points: 150,
          flag: 'flag{br0k3n_4cc3ss_4dm1n_p4n3l}'
        },
        {
          id: 'hash',
          slug: 'hash',
          name: 'Hash Cracking',
          description: 'Crack the leaked MD5 password hash.',
          category: 'Cryptography',
          difficulty: 'Easy',
          points: 75,
          flag: 'flag{md5_h4sh_cr4ck3d_3z}'
        },
        {
          id: 'rsa',
          slug: 'rsa',
          name: 'RSA Decryption',
          description: 'Decrypt the RSA ciphertext.',
          category: 'Cryptography',
          difficulty: 'Hard',
          points: 200,
          flag: 'flag{rs4_pr1v4t3_k3y_d3crypt3d}'
        },
        {
          id: 'bruteforce',
          slug: 'bruteforce',
          name: 'Brute Force Attack',
          description: 'Try the common password list.',
          category: 'Web Security',
          difficulty: 'Easy',
          points: 100,
          flag: 'flag{br0t3_f0rc3_w34k_p4ssw0rd}'
        },
        {
          id: 'diffie',
          slug: 'diffie',
          name: 'Diffie-Hellman Key Exchange',
          description: 'Compute the shared secret.',
          category: 'Cryptography',
          difficulty: 'Hard',
          points: 200,
          flag: 'flag{d1ff13_h3llm4n_k3y_3xch4ng3}'
        },
        {
          id: 'vigenere',
          slug: 'vigenere',
          name: 'Vigenere Cipher Decryption',
          description: 'Decrypt the Vigenere ciphertext.',
          category: 'Cryptography',
          difficulty: 'Medium',
          points: 150,
          flag: 'flag{v1g3n3r3_c1ph3r_cr4ck3d}'
        },
        {
          id: 'caesar',
          slug: 'caesar',
          name: 'Caesar Cipher',
          description: 'A short phrase was shifted by seven positions.',
          category: 'Cryptography',
          difficulty: 'Easy',
          points: 75,
          flag: 'flag{c4es4r_sh1ft_7_d3crypt3d}'
        },
        {
          id: 'crypto',
          slug: 'crypto',
          name: 'ROT13 Decryption',
          description: 'Decode the ROT13 text.',
          category: 'Cryptography',
          difficulty: 'Easy',
          points: 50,
          flag: 'flag{c4es4r_c1ph3r_r0t13_cr4ck3d}'
        }
      ];

    for (const challenge of challenges) {
      await Challenge.updateOne(
        { id: challenge.id },
        { $setOnInsert: challenge },
        { upsert: true }
      );
    }

    const total = await Challenge.countDocuments();
    if (total === 11) {
      console.log('✓ All 11 challenges are available');
    } else {
      console.log(`✓ Challenge sync complete (${total} stored docs)`);
    }

    // Create admin user if it doesn't exist
    const adminExists = await User.findOne({ username: process.env.ADMIN_USERNAME });
    if (!adminExists) {
      const adminUser = new User({
        publicId: 1,
        username: process.env.ADMIN_USERNAME,
        email: 'admin@ctf.local',
        password: process.env.ADMIN_PASSWORD,
        isAdmin: true,
        secretData: 'flag{1d0r_pr0f1l3_3num3r4t10n}'
      });
      await adminUser.save();
      console.log('✓ Admin user created');
    } else {
      await User.updateOne(
        { username: process.env.ADMIN_USERNAME },
        { $set: { publicId: 1, secretData: 'flag{1d0r_pr0f1l3_3num3r4t10n}' } }
      );
    }

    await User.updateOne(
      { username: 'player1' },
      { $set: { publicId: 2 } }
    );

    const usersMissingPublicId = await User.find({
      $or: [{ publicId: { $exists: false } }, { publicId: null }]
    }).sort({ createdAt: 1 });

    const highestPublicIdUser = await User.findOne({ publicId: { $exists: true, $ne: null } })
      .sort({ publicId: -1 })
      .select('publicId');
    let nextPublicId = highestPublicIdUser?.publicId || 2;

    for (const user of usersMissingPublicId) {
      nextPublicId += 1;
      user.publicId = nextPublicId;
      await user.save();
    }
  } catch (err) {
    console.error('Error initializing challenges:', err);
  }
};

// Start server
const PORT = process.env.PORT || 5000;

const startServer = async () => {
  try {
    // Wait for database connection
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Initialize challenges
    await initializeChallenges();
    
    const server = app.listen(PORT, () => {
      console.log(`Server running on http://localhost:${PORT}`);
    });

    server.on('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        console.error(`Port ${PORT} is already in use. Stop the other process or change PORT in backend/.env.`);
        process.exit(0);
      }

      throw err;
    });
  } catch (err) {
    console.error('Failed to start server:', err);
    process.exit(1);
  }
};

startServer();

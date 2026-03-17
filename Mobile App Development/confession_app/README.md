# Confessions App

A Flutter-based anonymous confession platform where university students can share thoughts, receive feedback, and build community while controlling their anonymity.

## 📱 Features (40% Midterm Implementation)

### ✅ Implemented Features

#### 1. **Authentication System**
- User registration with university selection
- Email and password login
- Session management
- Account creation for multiple universities

#### 2. **User Profiles**
- Personal profile view with user stats (posts, likes, joined date)
- Profile editing with anonymity control
- Option to reveal identity (name, university, bio)
- Profile picture placeholder with initials
- View other users' public profiles

#### 3. **Confession Posts**
- Create text-based confessions (max 280 characters)
- Toggle anonymous posting
- Edit own posts
- Delete own posts
- View post feed with newest first
- Post metadata (timestamp, author info)

#### 4. **Interactions**
- Like/Unlike posts with like counter
- Add comments to confessions (anonymous by default)
- View all comments on a post
- Comment count tracking
- Real-time interaction updates

#### 5. **Content Moderation (Automated)**
- Basic keyword filtering for flagged content
- Auto-flag posts containing inappropriate keywords
- Manual report system by users
- 3-report threshold for automatic suspension
- Status badges showing flagged content

#### 6. **User Interface**
- Clean, modern Material Design
- Deep purple color scheme
- Navigation with bottom bar (Feed, Search, Notifications)
- Floating action button for creating posts
- Responsive layouts for all screen sizes
- Loading states and error handling

## 🏗️ Project Structure

```
lib/
├── main.dart                 # App entry point with providers
├── models/
│   ├── user.dart            # User model
│   ├── post.dart            # Post model with status
│   └── comment.dart         # Comment model
├── services/
│   ├── auth_service.dart    # Authentication & user management
│   └── post_service.dart    # Post & moderation logic
├── screens/
│   ├── auth/
│   │   ├── login_screen.dart
│   │   └── signup_screen.dart
│   ├── home/
│   │   └── home_screen.dart
│   ├── post/
│   │   ├── create_post_screen.dart
│   │   └── post_detail_screen.dart
│   └── profile/
│       ├── profile_screen.dart
│       └── edit_profile_screen.dart
└── widgets/
    ├── post_card.dart       # Reusable post component
    └── comment_widget.dart  # Comment display component
```

## 🔧 Technologies Used

- **Framework**: Flutter 3.0+
- **Language**: Dart 3.0+
- **State Management**: Provider
- **Local Storage**: SQLite (ready for integration)
- **Backend Ready**: Firebase setup in pubspec.yaml

## 🚀 Getting Started

### Prerequisites
- Flutter SDK (3.0 or higher)
- Dart SDK (3.0 or higher)
- Android Studio / Xcode for emulators

### Installation

1. **Clone or navigate to project directory**
   ```bash
   cd confession_app
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Run the app**
   ```bash
   flutter run
   ```

## 📋 Testing the App

### Test Accounts (Pre-created in mock storage)
Currently uses in-memory mock database. You can register new accounts with:
- Email: any valid format
- Password: minimum 6 characters
- University: Select from dropdown list
- Username: Unique identifier

### Key Flows to Test

1. **Authentication**
   - Sign up new account
   - Login with credentials
   - Logout functionality

2. **Posts**
   - Create anonymous confession
   - Create named confession (toggle anonymity)
   - Like/unlike posts
   - View like counts

3. **Comments**
   - Add comment to post
   - View all comments
   - Comments remain anonymous

4. **Profile**
   - View own profile
   - Edit profile information
   - Toggle anonymity
   - View posts by user

5. **Moderation**
   - Try posting with keywords: "sexual", "racist", "explicit"
   - Report posts (3 reports flags post)
   - View flagged status on posts

## 📊 Data Models

### User
- `id` (unique identifier)
- `email`, `username` (unique)
- `university`
- `fullName`, `bio`, `profileImageUrl` (optional)
- `isAnonymous` (boolean)
- `createdAt` (timestamp)

### Post
- `id` (unique identifier)
- `userId` (author)
- `content` (text, max 280 chars)
- `imageUrl` (optional)
- `likeCount`, `commentCount` (tracked)
- `status` (active, flagged, suspended, deleted)
- `reports` (user IDs), `reportCount` (counter)
- `createdAt`, `updatedAt` (timestamps)

### Comment
- `id` (unique identifier)
- `postId`, `userId`
- `content` (text)
- `isAnonymous` (boolean)
- `likeCount`, `createdAt` (timestamp)

## 🔮 Planned Features (60% for Finals)

1. **Database Integration**
   - SQLite for local storage
   - Firebase/Cloud backend
   - Data sync and offline support

2. **Advanced Moderation**
   - Admin dashboard
   - Manual content review
   - User banning system
   - Appeal process

3. **Search & Discovery**
   - Full-text search
   - Hashtag support
   - Trending confessions
   - Filter by university

4. **Notifications**
   - Comment notifications
   - Like notifications
   - Report status updates
   - Push notifications

5. **Social Features**
   - User blocking
   - Report history
   - Post bookmarks
   - Share to social media

6. **Analytics**
   - Post statistics
   - User engagement metrics
   - Moderation reports
   - Admin analytics

7. **Performance & Polish**
   - Image uploads
   - Video support
   - Dark mode
   - Localization
   - Accessibility improvements

## 🐛 Known Limitations (Midterm Build)

- In-memory storage (data lost on app restart)
- No image upload functionality
- Mock password storage (for demo only)
- Limited search capability
- No push notifications
- Admin panel not included

## 📝 Code Quality

- Clean architecture with separation of concerns
- Service layer for business logic
- Reusable widget components
- Error handling throughout
- Loading states for async operations
- Comments and documentation

## 👥 Contributors

- Team members: [Add names]
- Project for: [University/Course]
- Academic Year: [Year]

## 📄 License

This project is for educational purposes.

---

**Note**: This is a 40% implementation focused on core features for midterm evaluation. The remaining 60% (database integration, advanced moderation, notifications, etc.) will be completed for the final submission.

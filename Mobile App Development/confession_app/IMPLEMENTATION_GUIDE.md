# Confessions App - Implementation Guide

## 🎯 Quick Start for Team

### Step 1: Setup Flutter Environment
```bash
# Ensure Flutter is installed
flutter --version

# Get project dependencies
cd confession_app
flutter pub get
```

### Step 2: Run the App
```bash
# For Android
flutter run -d android

# For iOS (macOS only)
flutter run -d ios

# For web (if enabled)
flutter run -d chrome
```

### Step 3: Create Test Account
1. Tap "Sign up" on login screen
2. Enter:
   - Email: `testuser@university.edu`
   - Username: `testuser`
   - Password: `password123`
   - Select University: `Harvard University`
3. Login with these credentials

### Step 4: Test Core Features
- ✅ Create a confession (FAB button)
- ✅ Toggle anonymous/named posting
- ✅ Like/unlike posts
- ✅ Add comments
- ✅ Edit your profile
- ✅ Report a post (menu icon)
- ✅ View user profiles

---

## 📂 File Architecture Guide

### `/lib/main.dart`
**Purpose**: App initialization and theme setup
**Key Components**:
- `MyApp` widget with Material theme
- Provider setup for AuthService and PostService
- Route to LoginScreen or HomeScreen based on auth state

### `/lib/models/`
**Data Models**:
- `user.dart`: User entity with serialization
- `post.dart`: Post with status tracking and reporting
- `comment.dart`: Comment with anonymity flag

### `/lib/services/`
**Business Logic**:
- `auth_service.dart`: User authentication, profile management
- `post_service.dart`: Post CRUD, likes, comments, moderation

### `/lib/screens/`
**UI Screens**:

#### Auth
- `auth/login_screen.dart`: Email/password login
- `auth/signup_screen.dart`: Registration with university

#### Home
- `home/home_screen.dart`: Main navigation hub with 3 tabs:
  - Feed: Display all active posts
  - Search: Placeholder for search feature
  - Notifications: Placeholder for notifications

#### Posts
- `post/create_post_screen.dart`: Confession creation with anonymity toggle
- `post/post_detail_screen.dart`: Full post view with comments and interactions

#### Profile
- `profile/profile_screen.dart`: View profile, stats, user's posts
- `profile/edit_profile_screen.dart`: Update profile, toggle anonymity

### `/lib/widgets/`
**Reusable Components**:
- `post_card.dart`: Post display with interactions
- `comment_widget.dart`: Comment display with author info

---

## 🔄 Data Flow Architecture

```
┌─────────────────────────────────────┐
│         Flutter UI Screens          │
│  (Login, Home, Posts, Profile)      │
└────────────┬────────────────────────┘
             │ notifyListeners()
             ↓
┌─────────────────────────────────────┐
│      Provider State Management      │
│  (AuthService, PostService)         │
└────────────┬────────────────────────┘
             │ Model Updates
             ↓
┌─────────────────────────────────────┐
│        Data Models (DTOs)           │
│  (User, Post, Comment)              │
└────────────┬────────────────────────┘
             │ Serialization
             ↓
┌─────────────────────────────────────┐
│   Mock Database (In-Memory)         │
│   → Future: SQLite/Firebase         │
└─────────────────────────────────────┘
```

---

## 🔐 Authentication Flow

```
Login/Signup → AuthService.login()/register()
                    ↓
              Validate credentials
                    ↓
         Store in mock database
                    ↓
         Update currentUser state
                    ↓
         notifyListeners() → redirect to HomeScreen
```

---

## 📝 Creating a Post Flow

```
User taps FAB
     ↓
CreatePostScreen opens
     ↓
User writes content, toggles anonymity
     ↓
POST button → PostService.createPost()
     ↓
Content moderation check
     ↓
Post added to _posts list
     ↓
notifyListeners() → HomeScreen rebuilds
```

---

## 💬 Comments System

```
User taps comment button on post
     ↓
PostDetailScreen shows comment input
     ↓
User enters comment text, taps send
     ↓
PostService.addComment() is called
     ↓
Comment added to _comments[postId]
     ↓
post.commentCount incremented
     ↓
ListView rebuilds to show new comment
```

---

## 🚨 Content Moderation System

### Automatic Flagging
```
User creates post with flagged keywords
          ↓
_checkContentForModeration() returns true
          ↓
post.status = PostStatus.flagged
          ↓
Post appears with "Flagged for review" badge
```

### Manual Reporting
```
User taps menu → Report
          ↓
Dialog confirmation
          ↓
PostService.reportPost(postId, userId)
          ↓
post.reports.add(userId)
          ↓
post.reportCount++
          ↓
If reportCount >= 3:
    post.status = PostStatus.flagged
```

---

## 🔧 Key Service Methods

### AuthService
```dart
// User Management
register(email, password, username, university) → bool
login(email, password) → bool
logout() → void
updateProfile(fullName, bio, profileImageUrl, isAnonymous) → bool
toggleAnonymity() → bool
getUserById(userId) → User?
```

### PostService
```dart
// Post Operations
createPost(userId, content, imageUrl) → String (postId)
updatePost(postId, userId, content) → bool
deletePost(postId, userId) → bool
getActivePosts() → List<Post>

// Interactions
toggleLike(postId, userId) → bool
hasUserLiked(postId, userId) → bool
addComment(postId, userId, content) → bool
getPostComments(postId) → List<Comment>

// Moderation
reportPost(postId, userId) → bool
unsuspendPost(postId) → bool
adminDeletePost(postId) → bool
_checkContentForModeration(content) → bool
```

---

## 🧪 Testing Checklist

### Authentication
- [ ] Register new account
- [ ] Login with correct credentials
- [ ] Login fails with wrong password
- [ ] Logout clears session
- [ ] Can view profile after login

### Posts
- [ ] Create anonymous confession
- [ ] Create named confession
- [ ] Post appears immediately in feed
- [ ] Can edit own post
- [ ] Can delete own post
- [ ] Cannot edit/delete others' posts
- [ ] Post appears with latest timestamp

### Interactions
- [ ] Can like a post
- [ ] Like counter increments
- [ ] Can unlike a post
- [ ] Cannot like same post twice
- [ ] Like persists in memory

### Comments
- [ ] Can add comment to post
- [ ] Comment appears in detail view
- [ ] Comment counter increments
- [ ] Multiple comments display correctly
- [ ] Comments are anonymous by default

### Moderation
- [ ] Posts with "sexual" keyword auto-flag
- [ ] Posts with "racist" keyword auto-flag
- [ ] Flagged posts show badge
- [ ] Can report a post
- [ ] Report counter increments
- [ ] 3 reports triggers flag status

### Profile
- [ ] View own profile
- [ ] View other user profiles
- [ ] Edit full name when named
- [ ] Toggle anonymity hides/shows info
- [ ] Posts count accurate
- [ ] Logout button works

---

## 📦 Dependencies Explained

| Package | Purpose |
|---------|---------|
| `provider` | State management |
| `sqflite` | Local database (ready for integration) |
| `path_provider` | File system access |
| `firebase_core` | Firebase setup (ready) |
| `firebase_auth` | Auth backend (ready) |
| `cloud_firestore` | Database backend (ready) |
| `firebase_storage` | Image storage (ready) |
| `google_fonts` | Typography |
| `cached_network_image` | Image caching |
| `intl` | Internationalization |
| `uuid` | Unique IDs |

---

## 🎨 UI/UX Guidelines

### Color Scheme
- **Primary**: `Colors.deepPurple` (#512da8)
- **Accent**: `Colors.red` (for likes)
- **Success**: `Colors.green`
- **Warning**: `Colors.orange`
- **Error**: `Colors.red`
- **Background**: `Colors.white`

### Typography
- **Headlines**: Roboto, FontWeight.bold
- **Body**: Roboto, normal weight
- **Caption**: Roboto, size 12

### Spacing
- Standard padding: 16px
- Card margins: 12px
- Item spacing: 8-16px

---

## 🚀 Deployment Preparation

### Before Submitting
1. Run `flutter analyze` - fix any linting issues
2. Test on both Android and iOS emulators
3. Clear mock data and test fresh installation
4. Verify all screens render correctly
5. Check error handling
6. Review code for comments

### Build Commands
```bash
# Debug build
flutter build apk --debug
flutter build ios --debug

# Release build (for finals)
flutter build apk --release
flutter build ios --release
```

---

## 📋 Team Collaboration Tips

### Code Review Checklist
- [ ] Code follows Dart conventions
- [ ] No hardcoded values
- [ ] Error handling implemented
- [ ] Loading states present
- [ ] Comments explain complex logic
- [ ] No console errors/warnings

### Git Commit Messages
```
[FEATURE] Add post creation screen
[FIX] Handle null user in profile view
[REFACTOR] Extract post card to widget
[DOCS] Update README with setup instructions
[TEST] Add login validation tests
```

### Branch Strategy
```
main (stable)
├── develop (integration)
│   ├── feature/auth-system
│   ├── feature/post-creation
│   └── feature/commenting
└── hotfix/bug-fix
```

---

## 🎓 Learning Resources

### For Team Members
- [Flutter Fundamentals](https://flutter.dev/docs)
- [Dart Language Guide](https://dart.dev/guides)
- [Provider Package Tutorial](https://pub.dev/packages/provider)
- [Material Design in Flutter](https://flutter.dev/docs/development/ui/material)

### Recommended Practices
- Keep widgets small (< 300 lines)
- Use const constructors where possible
- Extract reusable widgets
- Keep business logic in services
- Use meaningful variable names

---

## 📞 Troubleshooting

### App won't start
```bash
flutter clean
flutter pub get
flutter run
```

### Build errors
```bash
flutter pub get --offline
flutter pub cache clean
flutter pub get
flutter build apk
```

### State issues
- Check that Provider is wrapping the app
- Verify `notifyListeners()` is called
- Check Consumer widget is in the right place

### Navigation problems
- Ensure screens are properly imported
- Check MaterialPageRoute wrapping
- Verify Navigator.pop() is called correctly

---

## 🎯 Next Steps for Finals

1. **Implement Database**
   - Switch from mock to SQLite
   - Add data persistence

2. **Backend Integration**
   - Setup Firebase project
   - Migrate to Cloud Firestore
   - Implement real authentication

3. **Advanced Features**
   - Admin dashboard
   - Advanced search
   - Notifications
   - Image uploads

4. **Testing**
   - Write unit tests
   - Add widget tests
   - Integration testing

5. **Polish**
   - Dark mode support
   - Performance optimization
   - Accessibility improvements
   - App store deployment

---

**Last Updated**: May 3, 2026  
**Midterm Target**: 70-80%  
**Finals Target**: 90%+

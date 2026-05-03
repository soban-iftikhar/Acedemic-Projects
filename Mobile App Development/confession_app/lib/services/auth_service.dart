import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../models/user.dart';

class AuthService extends ChangeNotifier {
  User? _currentUser;
  bool _isLoggedIn = false;
  Map<String, User> _users = {}; // Mock database
  Map<String, String> _passwords = {}; // Mock password storage (in real app, use Firebase)

  User? get currentUser => _currentUser;
  bool get isLoggedIn => _isLoggedIn;

  /// Register a new user
  Future<bool> register({
    required String email,
    required String password,
    required String username,
    required String university,
  }) async {
    try {
      // Validate inputs
      if (email.isEmpty || password.isEmpty || username.isEmpty || university.isEmpty) {
        return false;
      }

      // Check if user already exists
      if (_users.values.any((u) => u.email == email || u.username == username)) {
        return false;
      }

      final userId = const Uuid().v4();
      final newUser = User(
        id: userId,
        email: email,
        username: username,
        university: university,
        createdAt: DateTime.now(),
      );

      _users[userId] = newUser;
      _passwords[email] = password;
      _currentUser = newUser;
      _isLoggedIn = true;

      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  /// Login user
  Future<bool> login({
    required String email,
    required String password,
  }) async {
    try {
      final user = _users.values.firstWhere(
        (u) => u.email == email,
        orElse: () => throw Exception('User not found'),
      );

      if (_passwords[email] != password) {
        return false;
      }

      _currentUser = user;
      _isLoggedIn = true;
      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  /// Logout user
  Future<void> logout() async {
    _currentUser = null;
    _isLoggedIn = false;
    notifyListeners();
  }

  /// Update user profile
  Future<bool> updateProfile({
    String? fullName,
    String? bio,
    String? profileImageUrl,
    bool? isAnonymous,
  }) async {
    try {
      if (_currentUser == null) return false;

      final updatedUser = User(
        id: _currentUser!.id,
        email: _currentUser!.email,
        username: _currentUser!.username,
        university: _currentUser!.university,
        fullName: fullName ?? _currentUser!.fullName,
        profileImageUrl: profileImageUrl ?? _currentUser!.profileImageUrl,
        bio: bio ?? _currentUser!.bio,
        isAnonymous: isAnonymous ?? _currentUser!.isAnonymous,
        createdAt: _currentUser!.createdAt,
      );

      _users[_currentUser!.id] = updatedUser;
      _currentUser = updatedUser;
      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  /// Get user by ID (for viewing other profiles)
  User? getUserById(String userId) {
    return _users[userId];
  }

  /// Toggle anonymity
  Future<bool> toggleAnonymity() async {
    try {
      if (_currentUser == null) return false;
      return updateProfile(isAnonymous: !_currentUser!.isAnonymous);
    } catch (e) {
      return false;
    }
  }
}

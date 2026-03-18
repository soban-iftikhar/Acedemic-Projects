import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../models/post.dart';
import '../models/comment.dart';

class PostService extends ChangeNotifier {
  List<Post> _posts = []; // Mock database
  Map<String, List<Comment>> _comments = {}; // comments per post
  Map<String, Set<String>> _userLikes = {}; // userId -> Set of postIds they liked
  
  List<Post> get posts => _posts;

  /// Create a new post
  Future<String> createPost({
    required String userId,
    required String content,
    String? imageUrl,
    bool userIsAnonymous = true,
  }) async {
    try {
      if (content.trim().isEmpty) throw Exception('Content cannot be empty');

      final postId = const Uuid().v4();
      final newPost = Post(
        id: postId,
        userId: userId,
        content: content,
        imageUrl: imageUrl,
        createdAt: DateTime.now(),
        status: _checkContentForModeration(content) ? PostStatus.flagged : PostStatus.active,
        userWasAnonymous: userIsAnonymous,
      );

      _posts.insert(0, newPost); // Add to top of list
      _comments[postId] = [];
      notifyListeners();
      return postId;
    } catch (e) {
      rethrow;
    }
  }

  /// Get all active posts for feed
  List<Post> getActivePosts() {
    return _posts.where((p) => p.status == PostStatus.active).toList();
  }

  /// Update a post
  Future<bool> updatePost({
    required String postId,
    required String userId,
    required String content,
  }) async {
    try {
      final postIndex = _posts.indexWhere((p) => p.id == postId);
      if (postIndex == -1) return false;

      if (_posts[postIndex].userId != userId) return false; // User can only edit their own posts

      final oldPost = _posts[postIndex];
      final updatedPost = Post(
        id: oldPost.id,
        userId: oldPost.userId,
        content: content,
        imageUrl: oldPost.imageUrl,
        createdAt: oldPost.createdAt,
        updatedAt: DateTime.now(),
        likeCount: oldPost.likeCount,
        commentCount: oldPost.commentCount,
        status: _checkContentForModeration(content) 
            ? PostStatus.flagged 
            : PostStatus.active,
        reports: oldPost.reports,
        reportCount: oldPost.reportCount,
      );
      _posts[postIndex] = updatedPost;

      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  /// Delete a post
  Future<bool> deletePost({
    required String postId,
    required String userId,
  }) async {
    try {
      final post = _posts.firstWhere((p) => p.id == postId);
      if (post.userId != userId) return false; // User can only delete their own posts

      _posts.removeWhere((p) => p.id == postId);
      _comments.remove(postId);
      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  /// Like/Unlike a post
  Future<bool> toggleLike({
    required String postId,
    required String userId,
  }) async {
    try {
      final post = _posts.firstWhere((p) => p.id == postId);
      _userLikes.putIfAbsent(userId, () => {});

      if (_userLikes[userId]!.contains(postId)) {
        _userLikes[userId]!.remove(postId);
        post.likeCount--;
      } else {
        _userLikes[userId]!.add(postId);
        post.likeCount++;
      }

      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  /// Check if user liked a post
  bool hasUserLiked(String postId, String userId) {
    return _userLikes[userId]?.contains(postId) ?? false;
  }

  /// Add a comment to a post
  Future<bool> addComment({
    required String postId,
    required String userId,
    required String content,
  }) async {
    try {
      final post = _posts.firstWhere((p) => p.id == postId);
      if (post.status != PostStatus.active) return false;

      final commentId = const Uuid().v4();
      final newComment = Comment(
        id: commentId,
        postId: postId,
        userId: userId,
        content: content,
        createdAt: DateTime.now(),
      );

      _comments[postId] ??= [];
      _comments[postId]!.add(newComment);
      post.commentCount++;

      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  /// Get comments for a post
  List<Comment> getPostComments(String postId) {
    return _comments[postId] ?? [];
  }

  /// Report a post (3 reports trigger auto-flag)
  Future<bool> reportPost({
    required String postId,
    required String userId,
  }) async {
    try {
      final post = _posts.firstWhere((p) => p.id == postId);

      if (!post.reports.contains(userId)) {
        post.reports.add(userId);
        post.reportCount++;

        if (post.reportCount >= 3) {
          post.status = PostStatus.flagged;
        }
      }

      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  /// Content moderation - checks for inappropriate keywords
  bool _checkContentForModeration(String content) {
    final flaggedWords = [
      'sexual', 'racist', 'explicit', 'hate', 'violence',
      // Add more flagged words as needed
    ];

    final lowerContent = content.toLowerCase();
    return flaggedWords.any((word) => lowerContent.contains(word));
  }

  /// Admin: Unsuspend a post
  Future<bool> unsuspendPost(String postId) async {
    try {
      final post = _posts.firstWhere((p) => p.id == postId);
      post.status = PostStatus.active;
      post.reportCount = 0;
      post.reports.clear();
      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  /// Admin: Delete a post
  Future<bool> adminDeletePost(String postId) async {
    try {
      _posts.removeWhere((p) => p.id == postId);
      _comments.remove(postId);
      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }
}

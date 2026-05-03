class Comment {
  final String id;
  final String postId;
  final String userId;
  final String content;
  DateTime createdAt;
  int likeCount;
  bool isAnonymous;

  Comment({
    required this.id,
    required this.postId,
    required this.userId,
    required this.content,
    required this.createdAt,
    this.likeCount = 0,
    this.isAnonymous = true,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'postId': postId,
      'userId': userId,
      'content': content,
      'createdAt': createdAt.toIso8601String(),
      'likeCount': likeCount,
      'isAnonymous': isAnonymous,
    };
  }

  factory Comment.fromMap(Map<String, dynamic> map) {
    return Comment(
      id: map['id'] as String,
      postId: map['postId'] as String,
      userId: map['userId'] as String,
      content: map['content'] as String,
      createdAt: DateTime.parse(map['createdAt'] as String),
      likeCount: map['likeCount'] as int? ?? 0,
      isAnonymous: map['isAnonymous'] as bool? ?? true,
    );
  }
}

enum PostStatus { active, flagged, suspended, deleted }

class Post {
  final String id;
  final String userId;
  final String content;
  String? imageUrl;
  DateTime createdAt;
  DateTime? updatedAt;
  int likeCount;
  int commentCount;
  PostStatus status;
  List<String> reports;
  int reportCount;
  bool userWasAnonymous; // Store anonymity state at time of post creation

  Post({
    required this.id,
    required this.userId,
    required this.content,
    this.imageUrl,
    required this.createdAt,
    this.updatedAt,
    this.likeCount = 0,
    this.commentCount = 0,
    this.status = PostStatus.active,
    this.reports = const [],
    this.reportCount = 0,
    this.userWasAnonymous = true,
  });

  bool isFlaggedForRemoval() => reportCount >= 3 || status == PostStatus.flagged;

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'userId': userId,
      'content': content,
      'imageUrl': imageUrl,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
      'likeCount': likeCount,
      'commentCount': commentCount,
      'status': status.toString(),
      'reports': reports,
      'reportCount': reportCount,
      'userWasAnonymous': userWasAnonymous,
    };
  }

  factory Post.fromMap(Map<String, dynamic> map) {
    return Post(
      id: map['id'] as String,
      userId: map['userId'] as String,
      content: map['content'] as String,
      imageUrl: map['imageUrl'] as String?,
      createdAt: DateTime.parse(map['createdAt'] as String),
      updatedAt: map['updatedAt'] != null 
          ? DateTime.parse(map['updatedAt'] as String) 
          : null,
      likeCount: map['likeCount'] as int? ?? 0,
      commentCount: map['commentCount'] as int? ?? 0,
      status: PostStatus.values.firstWhere(
        (e) => e.toString() == map['status'],
        orElse: () => PostStatus.active,
      ),
      reports: List<String>.from(map['reports'] as List? ?? []),
      reportCount: map['reportCount'] as int? ?? 0,
      userWasAnonymous: map['userWasAnonymous'] as bool? ?? true,
    );
  }
}

class User {
  final String id;
  final String email;
  final String username;
  String university;
  String? fullName;
  String? profileImageUrl;
  String? bio;
  bool isAnonymous;
  DateTime createdAt;

  User({
    required this.id,
    required this.email,
    required this.username,
    required this.university,
    this.fullName,
    this.profileImageUrl,
    this.bio,
    this.isAnonymous = true,
    required this.createdAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'email': email,
      'username': username,
      'university': university,
      'fullName': fullName,
      'profileImageUrl': profileImageUrl,
      'bio': bio,
      'isAnonymous': isAnonymous,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  factory User.fromMap(Map<String, dynamic> map) {
    return User(
      id: map['id'] as String,
      email: map['email'] as String,
      username: map['username'] as String,
      university: map['university'] as String,
      fullName: map['fullName'] as String?,
      profileImageUrl: map['profileImageUrl'] as String?,
      bio: map['bio'] as String?,
      isAnonymous: map['isAnonymous'] as bool? ?? true,
      createdAt: DateTime.parse(map['createdAt'] as String),
    );
  }
}

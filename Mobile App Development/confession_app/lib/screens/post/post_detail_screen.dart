import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/post_service.dart';
import '../../services/auth_service.dart';
import '../../models/post.dart';
import '../../widgets/comment_widget.dart';
import '../profile/profile_screen.dart';

class PostDetailScreen extends StatefulWidget {
  final String postId;

  const PostDetailScreen({Key? key, required this.postId}) : super(key: key);

  @override
  State<PostDetailScreen> createState() => _PostDetailScreenState();
}

class _PostDetailScreenState extends State<PostDetailScreen> {
  final _commentController = TextEditingController();
  bool _isSubmittingComment = false;

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  Future<void> _submitComment() async {
    if (_commentController.text.trim().isEmpty) return;

    setState(() => _isSubmittingComment = true);

    final postService = context.read<PostService>();
    final authService = context.read<AuthService>();

    final success = await postService.addComment(
      postId: widget.postId,
      userId: authService.currentUser!.id,
      content: _commentController.text,
    );

    if (mounted) {
      setState(() => _isSubmittingComment = false);
      if (success) {
        _commentController.clear();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Comment added')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final postService = context.read<PostService>();
    final authService = context.read<AuthService>();
    
    // Find the post
    Post? post;
    try {
      post = postService.posts.firstWhere((p) => p.id == widget.postId);
    } catch (e) {
      return Scaffold(
        appBar: AppBar(),
        body: const Center(child: Text('Post not found')),
      );
    }

    final comments = postService.getPostComments(widget.postId);
    final user = authService.getUserById(post!.userId);
    final hasLiked = postService.hasUserLiked(widget.postId, authService.currentUser!.id);

    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        title: const Text('Confession'),
        elevation: 0,
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Post card
            Card(
              margin: const EdgeInsets.all(12),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Author info
                    GestureDetector(
                      onTap: !post!.userWasAnonymous
                          ? () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) =>
                                      ProfileScreen(userId: post!.userId),
                                ),
                              );
                            }
                          : null,
                      child: Row(
                        children: [
                          CircleAvatar(
                            backgroundColor: Colors.deepPurple[100],
                            child: Text(
                              post!.userId.substring(0, 1).toUpperCase(),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  post!.userWasAnonymous
                                      ? 'Anonymous'
                                      : (user?.fullName ?? 'Anonymous'),
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                if (!post!.userWasAnonymous)
                                  Text(
                                    user?.university ?? '',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.grey[600],
                                    ),
                                  ),
                              ],
                            ),
                          ),
                          // Report feature coming soon
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Post content
                    Text(
                      post!.content,
                      style: const TextStyle(fontSize: 16),
                    ),
                    const SizedBox(height: 12),

                    // Timestamp and status
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          _formatTime(post!.createdAt),
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                        if (post!.status == PostStatus.flagged)
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.red[100],
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              'Flagged',
                              style: TextStyle(
                                fontSize: 10,
                                color: Colors.red[700],
                              ),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // Interaction buttons
                    Row(
                      children: [
                        _InteractionButton(
                          icon: hasLiked ? Icons.favorite : Icons.favorite_border,
                          label: '${post!.likeCount}',
                          color: hasLiked ? Colors.red : Colors.grey[600],
                          onTap: () async {
                            await postService.toggleLike(
                              postId: widget.postId,
                              userId: authService.currentUser!.id,
                            );
                            setState(() {});
                          },
                        ),
                        const SizedBox(width: 16),
                        _InteractionButton(
                          icon: Icons.comment_outlined,
                          label: '${comments.length}',
                          color: Colors.grey[600],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            // Comments section
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Text(
                'Comments (${comments.length})',
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),

            // Comments list
            comments.isEmpty
                ? Padding(
                    padding: const EdgeInsets.all(32),
                    child: Center(
                      child: Text(
                        'No comments yet',
                        style: TextStyle(color: Colors.grey[600]),
                      ),
                    ),
                  )
                : ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: comments.length,
                    itemBuilder: (context, index) {
                      return CommentWidget(comment: comments[index]);
                    },
                  ),
          ],
        ),
      ),
      bottomSheet: _buildCommentInput(),
    );
  }

  Widget _buildCommentInput() {
    return Container(
      padding: EdgeInsets.fromLTRB(
        16,
        12,
        16,
        MediaQuery.of(context).viewInsets.bottom + 12,
      ),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(top: BorderSide(color: Colors.grey[300]!)),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _commentController,
              decoration: InputDecoration(
                hintText: 'Add a comment...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            onPressed: _isSubmittingComment ? null : _submitComment,
            icon: _isSubmittingComment
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.send),
            color: Colors.deepPurple,
          ),
        ],
      ),
    );
  }

  String _formatTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inMinutes < 1) {
      return 'just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h ago';
    } else {
      return '${difference.inDays}d ago';
    }
  }
}

class _InteractionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color? color;
  final VoidCallback? onTap;

  const _InteractionButton({
    required this.icon,
    required this.label,
    this.color,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(color: color, fontSize: 12),
          ),
        ],
      ),
    );
  }
}

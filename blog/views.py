from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Count, Prefetch, Min


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': post.tags.all(),
        'first_tag_title': post.first_tag,
        }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def index(request):
    most_popular_posts = Post.objects.popular()[:5]. \
        fetch_with_comments_count(). \
        prefetch_related('author').prefetch_related('tags').\
        fetch_with_tags_title()

    most_fresh_posts = Post.objects.order_by('-published_at')[:5]. \
        fetch_with_comments_count(). \
        prefetch_related('author').prefetch_related('tags').\
        fetch_with_tags_title()

    most_popular_tags = Tag.objects.popular()[:5].\
        prefetch_related(Prefetch('posts')).\
        annotate(posts_count=Count('posts'))

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.get(slug=slug)
    comments = Comment.objects.filter(post=post).prefetch_related('author')
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes = post.likes.all()

    related_tags = post.tags.all().prefetch_related('posts')

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': likes.count(),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [tag for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5].prefetch_related('posts')

    most_popular_posts = Post.objects.popular()[:5]. \
        fetch_with_comments_count(). \
        prefetch_related('author').prefetch_related('tags').\
        fetch_with_tags_title()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5].prefetch_related('posts')

    most_popular_posts = Post.objects.popular()[:5]. \
        fetch_with_comments_count(). \
        prefetch_related('author').prefetch_related('tags').\
        fetch_with_tags_title()

    related_posts = tag.posts.all()[:20]. \
        fetch_with_comments_count(). \
        prefetch_related('author').prefetch_related('tags').\
        fetch_with_tags_title()

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})

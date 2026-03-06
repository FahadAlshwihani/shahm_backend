from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Category, Tag, BlogPost, BlogPageSettings
from .serializers import CategorySerializer, TagSerializer, BlogPostSerializer, BlogPageSettingsSerializer
from accounts.permissions import IsEditorOrAbove



# ================================
# PUBLIC VIEW — BLOG LIST
# ================================
class PublicBlogListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        post_type = request.GET.get("type")

        posts = BlogPost.objects.filter(
            status="published"
        )

        if post_type:
            posts = posts.filter(post_type=post_type)

        posts = posts.order_by("-publish_date", "-created_at")

        serializer = BlogPostSerializer(
            posts, many=True, context={"request": request}
        )
        return Response(serializer.data)



# ================================
# PUBLIC VIEW — BLOG DETAILS
# ================================
class PublicBlogDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        try:
            post = BlogPost.objects.get(slug=slug, status="published")
        except BlogPost.DoesNotExist:
            return Response({"detail": "Post not found"}, status=404)

        post.views_count += 1
        post.save()

        serializer = BlogPostSerializer(
            post, context={"request": request}
        )
        return Response(serializer.data)


# ================================
# PUBLIC — LIST CATEGORIES
# ================================
class PublicCategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.all()
        return Response(
            CategorySerializer(categories, many=True).data
        )


# ================================
# PUBLIC — LIST TAGS
# ================================
class PublicTagListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        tags = Tag.objects.all()
        return Response(
            TagSerializer(tags, many=True).data
        )


# ================================
# ADMIN — CATEGORIES
# ================================
class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        categories = Category.objects.all()
        return Response(
            CategorySerializer(categories, many=True).data
        )

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class CategoryDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        try:
            category = Category.objects.get(id=pk)
        except Category.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        serializer = CategorySerializer(
            category, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            category = Category.objects.get(id=pk)
        except Category.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        category.delete()
        return Response(status=204)


# ================================
# ADMIN — TAGS
# ================================
class TagListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        tags = Tag.objects.all()
        return Response(
            TagSerializer(tags, many=True).data
        )

    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class TagDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        try:
            tag = Tag.objects.get(id=pk)
        except Tag.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        serializer = TagSerializer(
            tag, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            tag = Tag.objects.get(id=pk)
        except Tag.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        tag.delete()
        return Response(status=204)


# ================================
# ADMIN — BLOG POSTS
# ================================
class BlogListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        post_type = request.GET.get("type")

        posts = BlogPost.objects.all()

        if post_type:
            posts = posts.filter(post_type=post_type)

        posts = posts.order_by("-created_at")

        serializer = BlogPostSerializer(
            posts, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = BlogPostSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class BlogDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request, pk):
        try:
            post = BlogPost.objects.get(id=pk)
        except BlogPost.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        serializer = BlogPostSerializer(
            post, context={"request": request}
        )
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            post = BlogPost.objects.get(id=pk)
        except BlogPost.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        serializer = BlogPostSerializer(
            post,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            post = BlogPost.objects.get(id=pk)
        except BlogPost.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        post.delete()
        return Response(status=204)


class PublicBlogSettingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        settings = BlogPageSettings.objects.first()
        if not settings:
            return Response({})
        serializer = BlogPageSettingsSerializer(settings)
        return Response(serializer.data)


class BlogSettingsUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request):
        settings = BlogPageSettings.objects.first()

        if not settings:
            settings = BlogPageSettings.objects.create()

        serializer = BlogPageSettingsSerializer(
            settings,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

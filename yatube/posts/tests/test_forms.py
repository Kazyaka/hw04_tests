from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(
            username='post_author',
        )
        cls.non_post_author = User.objects.create_user(
            username='non_post_author',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )

    def setUp(self):
        self.guest_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.post_author)
        self.authorized_user_second = Client()
        self.authorized_user_second.force_login(self.non_post_author)

    def test_authorized_user_create_post(self):
        """Проверка создания поста авторизованным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.post_author.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.group_id, form_data['group'])

    def test_authorized_user_edit_post(self):
        """Проверка редактирования поста авторизованным пользователем."""
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.post_author,
            group=self.group,
        )
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            reverse(
                'posts:post_edit',
                args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        created_post = Post.objects.get(id=post.id)
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.author, post.author)
        self.assertEqual(created_post.group_id, form_data['group'])
        self.assertEqual(created_post.pub_date, post.pub_date)

    def test_nonauthorized_user_create_post(self):
        """Проверка создания поста неавторизованным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response = self.guest_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse('login') + '?next=' + reverse('posts:post_create')
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_nonauthorized_user_edit_post(self):
        """Проверка редактирования поста неавторизованным пользователем."""
        posts_count = Post.objects.count()
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.post_author,
            group=self.group,
        )
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }
        response = self.guest_user.post(
            reverse(
                'posts:post_edit',
                args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        edited_post = Post.objects.get(id=post.id)
        redirect = reverse('login') + '?next=' + reverse('posts:post_edit',
                                                         kwargs={'post_id':
                                                                 post.id})
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(edited_post.pub_date, post.pub_date)
        self.assertEqual(edited_post.author, post.author)
        self.assertEqual(edited_post.text, post.text)
        self.assertEqual(edited_post.group, post.group)

    def test_authorized_user_not_edit_post(self):
        """Проверка что авт. пользователь не сможет редатировать чужой пост."""
        posts_count = Post.objects.count()
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.post_author,
            group=self.group,
        )
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }
        response = self.authorized_user_second.post(
            reverse(
                'posts:post_edit',
                args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse('posts:post_detail', kwargs={'post_id': post.id})
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        edited_post = Post.objects.get(id=post.id)
        self.assertEqual(post.text, edited_post.text)
        self.assertEqual(post.author, edited_post.author)
        self.assertEqual(post.group, edited_post.group)
        self.assertEqual(post.pub_date, edited_post.pub_date)

    def test_authorized_user_create_post_without_group(self):
        """Проверка создания поста авторизованным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.post_author.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.group, None)

from django import forms


from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_posts',
                                             kwargs={'slug': 'test-slug'}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username':
                                                  self.user.username}),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': '1'})
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        task_group_0 = first_object.group
        self.assertEqual(task_text_0, self.post.text)
        self.assertEqual(task_author_0, self.post.author)
        self.assertEqual(task_group_0, self.post.group)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse
                                              ('posts:group_posts',
                                               kwargs={'slug':
                                                       self.group.slug}))
        first_object = response.context['page_obj'][0]
        group_of_post = response.context['group']
        task_title = group_of_post.title
        task_slug = group_of_post.slug
        task_description = group_of_post.description
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        task_group_0 = first_object.group
        self.assertEqual(task_text_0, self.post.text)
        self.assertEqual(task_author_0, self.post.author)
        self.assertEqual(task_group_0, self.post.group)
        self.assertEqual(task_title, self.group.title)
        self.assertEqual(task_slug, self.group.slug)
        self.assertEqual(task_description, self.group.description)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:profile',
                                                      kwargs={'username':
                                                              self.user}))
        first_object = response.context['page_obj'][0]
        author_of_post = response.context['author']
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        task_group_0 = first_object.group
        self.assertEqual(task_text_0, self.post.text)
        self.assertEqual(task_author_0, self.post.author)
        self.assertEqual(task_group_0, self.post.group)
        self.assertEqual(author_of_post, self.post.author)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                                      kwargs={'post_id':
                                                              self.post.pk}))
        first_object = response.context['post']
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        task_group_0 = first_object.group
        self.assertEqual(task_text_0, self.post.text)
        self.assertEqual(task_author_0, self.post.author)
        self.assertEqual(task_group_0, self.post.group)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      kwargs={'post_id': '1'}))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                if value == reverse('posts:post_create'):
                    self.assertEqual(
                        response.context['is_edit'], False) 
                else:
                    self.assertEqual(
                        response.context['is_edit'], True) 

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_with_group_on_index_page(self):
        """Если при создании поста указать группу,"""
        """ пост появляется на главной странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj']
        self.assertIn(Post.objects.get(group=self.post.group), first_object)

    def test_post_with_group_on_group_list_page(self):
        """Если при создании поста указать группу,"""
        """ пост появляется на странице группы"""
        response = self.authorized_client.get(reverse('posts:group_posts',
                                              kwargs={'slug':
                                                      self.group.slug}))
        first_object = response.context['page_obj'][0]
        group = first_object.group.title
        self.assertEqual(group, self.group.title)

    def test_post_with_group_on_profile_page(self):
        """Если при создании поста указать группу,"""
        """ пост появляется на странице профиля"""
        response = self.authorized_client.get(reverse('posts:profile',
                                                      kwargs={'username':
                                                              self.user}))
        first_object = response.context['page_obj']
        self.assertIn(Post.objects.get(group=self.post.group), first_object)

    def test_post_not_in_wrong_group(self):
        """"Проверка что пост не ушел не в ту группу"""
        new_test_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='another_test-slug',
            description='Другое тестовое описание группы')
        new_test_url = reverse('posts:group_posts', args=[new_test_group.slug])
        response = self.authorized_client.get(new_test_url)
        self.assertNotIn(PostPagesTests.post, response.context['page_obj'])


FIRST_POST = 1
FINAL_POST = 16
POSTS_ON_FIRST_PAGE = 10
POSTS_ON_FINAL_PAGE = 5

class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_pag = User.objects.create_user(username='auth_pag')
        cls.group_pag = Group.objects.create(
            title='Тестовая группа для пагинатора',
            slug='test-slug_pag',
            description='Тестовое описание группы для пагинатора',
        )
        cls.post = Post.objects.bulk_create([
            Post(text='Тестовый текст поста',
                 author=cls.user_pag,
                 group=cls.group_pag,
                 )
            for i in range(FIRST_POST, FINAL_POST)])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_pag)

    def test_paginator_index_page(self):
        response_first = self.authorized_client.get(reverse('posts:index'))
        response_second = self.authorized_client.get(reverse('posts:index')
                                                     + '?page=2')
        self.assertEqual(len(response_first.context['page_obj']),
                         POSTS_ON_FIRST_PAGE)
        self.assertEqual(len(response_second.context['page_obj']),
                         POSTS_ON_FINAL_PAGE)

    def test_paginator_group_list_page(self):
        response_first = (self.authorized_client.get
                          (reverse('posts:group_posts',
                                   kwargs={'slug': self.group_pag.slug})))
        response_second = (self.authorized_client.get
                           (reverse('posts:group_posts',
                                    kwargs={'slug':
                                            self.group_pag.slug}) + '?page=2'))
        self.assertEqual(len(response_first.context['page_obj']),
                         POSTS_ON_FIRST_PAGE)
        self.assertEqual(len(response_second.context['page_obj']),
                         POSTS_ON_FINAL_PAGE)

    def test_paginator_profile_page(self):
        response_first = (self.authorized_client.get
                          (reverse('posts:profile',
                                   kwargs={'username': self.user_pag})))
        response_second = (self.authorized_client.get
                           (reverse('posts:profile',
                                    kwargs={'username':
                                            self.user_pag}) + '?page=2'))
        self.assertEqual(len(response_first.context['page_obj']), 10)
        self.assertEqual(len(response_second.context['page_obj']), 5)

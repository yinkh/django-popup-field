from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='名称')

    class Meta:
        verbose_name = '类别'
        verbose_name_plural = '类别'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255, verbose_name='名称')

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    category = models.ForeignKey('post.Category', related_name='post_category', on_delete=models.CASCADE,
                                 verbose_name='类别')
    tags = models.ManyToManyField('post.Tag',
                                  verbose_name='标签')

    class Meta:
        verbose_name = '帖子'
        verbose_name_plural = '帖子'

    def __str__(self):
        return self.title

from django.db import models
import uuid
from django.contrib import admin
from catalog.models import Category
# from university.models import University

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import os
import shutil

import deepzoom

from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO

from django.core.files.storage import default_storage

from django.forms.models import model_to_dict

import time

# Create your models here.
class Gist(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    section = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    is_hide = models.BooleanField(default=False)
    image = models.FileField(upload_to='gist_images/', blank=True, null=True)
    crop_image = models.FileField(upload_to='cropped_gist_images/', blank=True, null=True)
    dzi_image = models.FileField(upload_to='gist_images/', blank=True, null=True)
    marking = models.CharField(max_length=200000, blank=True, null=True)
    # university = models.ForeignKey(University, on_delete=models.CASCADE, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial = self._dict

    def save(self, *args, **kwargs):     
        super(Gist, self).save(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):        
        return self.diff.get(field_name, None)

    @admin.display(description='Имя препарата')
    def name_display(self):
        return self.name

    @admin.display(description='ID Раздела')
    def section_id_display(self):
        return self.section.uuid

    @admin.display(description='Относительный путь изображения')
    def image_display(self):
        return self.image
    
    @admin.display(description='Обрезанное изображения')
    def cropped_image_display(self):
        return self.crop_image
    
    @admin.display(description='Относительный путь dzi изображения')
    def dzi_image_display(self):
        return self.dzi_image
    
    @admin.display(description='Разметка гисты')
    def marking_display(self):
        return self.marking

    # @admin.display(description='Университет')
    # def university_display(self):
    #     return self.university

    def __str__(self):
        return f'<Gist obj> UUID:{self.uuid}'

    def to_json(self):
        return {
            "id": self.uuid,
            "name": self.name,
            "section": self.section.name,
            "image": self.get_image_url(),
            "dzi_image": self.get_dzi_image_url(),
            # "university": self.university,            
        }
    
    def get_deepzoom_folder_path(self):
        try:
            full_file_name = self.image.name.split('/')[1]
            file_name = 'image_{0}'.format(self.id)
            return self.image.path.replace(full_file_name, '{}_files'.format(file_name))
        except:
            return None
    
    def convert_image_to_dzi(self):
        print(self.image.name)
        
        full_file_name = self.image.name.split('/')[1]
        file_name = 'image_{0}'.format(self.id)
        ext = full_file_name.split('.')[1]
        dzi_output_path = './media/gist_images/' + file_name + '.dzi'

        useless_dir = self.image.path.replace(full_file_name, '{}_files'.format(file_name))
        try:
            shutil.rmtree(useless_dir)
        except:
            pass
        
        current_image_path = self.image.path
        current_image_dir = os.path.dirname(current_image_path)
        new_image_name = 'image_{0}.png'.format(self.id)
        new_image_path = os.path.join(current_image_dir, new_image_name)
        if default_storage.exists(new_image_path):
            os.remove(new_image_path)
        os.rename(current_image_path, new_image_path)

        self.image = 'gist_images/' + new_image_name   

        image_path = "file:///" + self.image.path
        creator = deepzoom.ImageCreator(resize_filter='bicubic', tile_format='png', tile_size=256, image_quality=0.9, tile_overlap=2)        
        creator.create(image_path, dzi_output_path)
        
        self.dzi_image = 'gist_images/' + file_name + '.dzi'

    def get_image_url(self):
        if self.image:
            return self.image.url
        return None
    
    def get_dzi_image_url(self):
        if self.dzi_image:
            return self.dzi_image.url
        return None

    

@receiver(post_save, sender=Gist)
def convert_image_to_dzi_on_save(sender, instance, created, **kwargs):  
    if created:
        instance.convert_image_to_dzi()
        prev_image = instance.image.path
        img_name = "image_{0}.png".format(instance.id)
        with Image.open(instance.image) as img:
            img_resized = img.resize((127, 116))
            image_io = BytesIO()
            img_resized.save(image_io, format=img.format)
            cropped_image_file = ContentFile(image_io.getvalue(), name=img_name)
        img.close()
        
        instance.image.save(img_name, cropped_image_file, save=False)
        os.remove(prev_image)

        current_image_path = instance.image.path
        current_image_dir = os.path.dirname(current_image_path)
        new_image_path = os.path.join(current_image_dir, img_name)        
        os.rename(current_image_path, new_image_path)
        instance.image = "gist_images/"+img_name
        
        post_save.disconnect(convert_image_to_dzi_on_save, sender=Gist)
        instance.save()
        post_save.connect(convert_image_to_dzi_on_save, sender=Gist)


@receiver(models.signals.post_delete, sender=Gist)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image and os.path.exists(instance.image.path):
        os.remove(instance.image.path)
    if instance.dzi_image and os.path.exists(instance.dzi_image.path):
        os.remove(instance.dzi_image.path)
    dzi_folder_path = instance.get_deepzoom_folder_path()
    if dzi_folder_path and os.path.exists(dzi_folder_path):
        shutil.rmtree(instance.get_deepzoom_folder_path())


@receiver(pre_save, sender=Gist)
def pre_save_image(sender, instance, *args, **kwargs):
    """ instance old image file will delete from os """
    try:
        old_img = instance.__class__.objects.get(id=instance.id).image.path
        try:
            new_img = instance.image.path
        except:
            new_img = None
        if new_img != old_img:
            import os
            if os.path.exists(old_img):
                os.remove(old_img)
    except:
        pass
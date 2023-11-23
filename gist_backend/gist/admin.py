from django.contrib import admin
from .models import Gist


# Register your models here.
@admin.register(Gist)
class GistAdmin(admin.ModelAdmin):
    list_display = ('name_display', 'section_id_display', 'image_display', 'dzi_image_display', 'marking_display', 'cropped_image_display')
    fields = ('name', 'section', 'image', 'dzi_image', 'crop_image', 'marking')
    search_fields = ('name__startswith',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["name"].label = "Название препарата"
        form.base_fields["section"].label = "ID раздела"
        form.base_fields['image'].label = "Изображение"
        form.base_fields['dzi_image'].label = "DZI Изображение"
        form.base_fields['crop_image'].label = "Обрезанное Изображение"
        form.base_fields['marking'].label = "Разметка"


        return form
    


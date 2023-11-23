from catalog.models import Category
from gist.models import Gist
from django.core.exceptions import ObjectDoesNotExist

def get_gists(category, user):
    ''' Получить все гисты, связанные с данной категорией и пользователем '''
    gists = Gist.objects.filter(section=category, is_hide=False).order_by('name')
    return [
        {
            'id': str(gist.uuid),
            'name': gist.name,
            'img': gist.get_image_url()
        } for gist in gists
    ]

def get_subsections(category, user):
    ''' Получить все подкатегории, связанные с данной категорией и пользователем '''
    subsections = Category.objects.filter(parent=category, owners__id=user.id).order_by('name')
    return [
        {
            'id': str(sub.uuid),
            'name': sub.name,
            'gists': get_gists(sub, user),
            'subsections': get_subsections(sub, user)
        } for sub in subsections
    ]

def get_sections(user):
    ''' Получить все корневые категории (те, у которых нет родителя), связанные с пользователем '''
    root_categories = Category.objects.filter(parent=None, owners__id=user.id).order_by('created_at')
    sections = [
        {
            'id': str(category.uuid),
            'name': category.name,
            'subsections': get_subsections(category, user),
            "gists": get_gists(category, user)
        } for category in root_categories
    ]
    return sections

def is_category_exists_at_same_level(name, user, parent_id=None):
    """
    Проверяет, существует ли уже категория с заданным именем на том же уровне вложенности.
    
    :param name: Имя категории для проверки.
    :param parent_id: ID родительской категории. Если None, то проверяется корневой уровень.
    :return: True, если категория существует на том же уровне, иначе False.
    """
    try:
        if parent_id:
            # Проверка существования категории с тем же именем и родителем
            Category.objects.get(name=name, parent_id=parent_id, owners__in=[user])
        else:
            # Проверка существования категории с тем же именем на корневом уровне
            Category.objects.get(name=name, parent__isnull=True, owners__in=[user])
        return True
    except ObjectDoesNotExist:
        return False
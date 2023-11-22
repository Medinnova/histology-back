from rolepermissions.roles import AbstractUserRole

class Admin(AbstractUserRole):
    available_permissions = {
        'add_teacher': False,
        'add_moderator': True,
        'delete_moderator': True,      
        'create_gists': True,
        'edit_gists': True,
        'delete_gists': True,
        'watch_statistics': True,
        'watch_paid_gists': True,
        'watch_university_gists': True,
    }

class Moderator(AbstractUserRole):
    available_permissions = {
        'add_moderator': True,
        'add_teacher': True,
        'delete_moderator': False,      
        'create_gists': False,
        'edit_gists': False,
        'delete_gists': False,
        'watch_statistics': False,
        'watch_paid_gists': True,
        'watch_university_gists': True,        
    }

class Teacher(AbstractUserRole):
    available_permissions = {
        'add_moderator': False,
        'add_teacher': False,
        'delete_moderator': False,      
        'create_gists': True,
        'edit_gists': True,
        'delete_gists': True,
        'watch_statistics': False,
        'watch_paid_gists': True,
        'watch_university_gists': True,        
    }

class Subscriber(AbstractUserRole):
    available_permissions = {          
        'add_teacher': False,
        'add_moderator': False,
        'delete_moderator': False,      
        'create_gists': False,
        'edit_gists': False,
        'delete_gists': False,
        'watch_statistics': False,
        'watch_paid_gists': True,
        'watch_university_gists': False,        
    }


class Student(AbstractUserRole):
    available_permissions = { 
        'add_teacher': False,
        'add_moderator': False,
        'delete_moderator': False,      
        'create_gists': False,
        'edit_gists': False,
        'delete_gists': False,
        'watch_statistics': False,
        'watch_paid_gists': True,
        'watch_university_gists': True,        
    }


class Default(AbstractUserRole):
    available_permissions = {  
        'add_teacher': False,
        'add_moderator': False,
        'delete_moderator': False,      
        'create_gists': False,
        'edit_gists': False,
        'delete_gists': False,
        'watch_statistics': False,   
        'watch_paid_gists': False,
        'watch_university_gists': False,     
    }
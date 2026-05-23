from users.models import User, RegistrationToken


def get_manager_stats():
    all_students = User.objects.filter(role=User.Role.STUDENT)
    return {
        'total_students': all_students.count(),
        'students_without_group': all_students.filter(group__isnull=True).count(),
        'active_invites': RegistrationToken.objects.filter(is_used=False).count(),
    }


def get_students():
    return (
        User.objects
        .filter(role=User.Role.STUDENT)
        .select_related('group')
        .order_by('last_name', 'first_name', 'username')
    )


def get_section_assignments():
    from courses.models import Section
    return Section.objects.prefetch_related('teachers').order_by('order')


def get_teachers():
    return User.objects.filter(role=User.Role.TEACHER).order_by('last_name', 'first_name')


def set_section_teachers(section, teacher_ids):
    section.teachers.set(teacher_ids)

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.urls import include, path, reverse_lazy
from django.views.generic.edit import CreateView

handler404 = 'pages.views.page_not_found'
handler403 = 'pages.views.csrf_failure'
handler500 = 'pages.views.server_error'


urlpatterns = [
    path('admin/', admin.site.urls),

    # Работа с пользователем:
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', CreateView.as_view(
        template_name='registration/registration_form.html',
        form_class=UserCreationForm,
        success_url=reverse_lazy('blog:index'),),
        name='registration',
    ),

    # Приложения:
    path('pages/', include('pages.urls')),
    path('', include('blog.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

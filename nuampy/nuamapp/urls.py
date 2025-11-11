from django.urls import path
from .views import login_view, logout_view, home_view, administracion_view, crear_usuario_view, modificar_usuario_view, eliminar_usuario_view,ingresar_calificacion_view,cargar_factores, cargar_montos

urlpatterns = [
    path('home/', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('administrar/', administracion_view, name='administrar'),
    path('administrar/crear-usuario/', crear_usuario_view, name='crear_usuario'),
    path('administrar/modificar-usuario/<str:usuario_id>/', modificar_usuario_view, name='modificar_usuario'),
    path('administrar/eliminar-usuario/<str:usuario_id>/', eliminar_usuario_view, name='eliminar_usuario'),
    path('ingresar-calificaciones/', ingresar_calificacion_view, name='ingresar_calificaciones'),
    path("cargar-factores/", cargar_factores, name="cargar_factores"),
    path("cargar-montos/", cargar_montos, name="cargar_montos"),
]

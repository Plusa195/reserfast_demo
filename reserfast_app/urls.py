from django.urls import path, include
from . import views
from . import admin_views
from django.contrib.auth import views as auth_views

app_name = 'reserfast'

urlpatterns = [
    path('', views.index, name='index'),
    path('index_admin/', views.index_admin, name='index_admin'),
    
    path('login_admin/', views.login_admin, name='login_admin'),
    path('login_clientes/', views.login_clientes, name='login_clientes'),
    path('logout_empleado/', views.logout_empleado, name='logout_empleado'),
    path('logout_cliente/', views.logout_cliente, name='logout_cliente'),
    path('panel_garzon/', views.panel_garzon, name='panel_garzon'),
    path('cambiar_password/', views.cambiar_password_empleado, name='cambiar_password_empleado'),
    path('editar_perfil_empleado/', views.editar_perfil_empleado, name='editar_perfil_empleado'),

    path('crear_cliente/', views.create_clientes, name='create_clientes'),
    path('crear_exito/', views.crear_exito, name='crear_exito'),
    path('index_cliente/', views.index_cliente, name='index_cliente'),
    path('menu/', views.menu_cliente, name='menu_cliente'),
    path('mesas/', views.mesa_cliente, name='mesas'),
    
    path('perfil/', views.perfil_cliente, name='perfil_cliente'),
    path('editar_perfil/', views.editar_perfil_cliente, name='editar_perfil_cliente'),

    path('admin_garzones/', views.listar_garzones, name='admin_garzones'),
    path('crear_garzones/', views.crear_garzones, name='agregar_garzones'),
    path('eliminar_garzones/<str:id_usuario>/', views.eliminar_garzones, name='eliminar_garzones'),
    path('actualizar_garzones/<str:id_usuario>/', views.actualizar_garzones, name='actualizar_garzones'),

    path('gestion_cocina/', views.gestion_cocina, name='gestion_cocina'),
    path('gestion_cocina/toggle_menu/<int:menu_id>/', views.toggle_menu_cocina, name='toggle_menu_cocina'),
    path('admin_cocina/', views.listar_usuarios_cocina, name='admin_cocina'),
    path('crear_usuarios_cocina/', views.crear_usuarios_cocina, name='crear_usuarios_cocina'),
    path('eliminar_usuarios_cocina/<str:id_usuario>/', views.eliminar_usuarios_cocina, name='eliminar_usuarios_cocina'),
    path('actualizar_usuarios_cocina/<str:id_usuario>/', views.actualizar_usuarios_cocina, name='actualizar_usuarios_cocina'),

    path('crear_venta/', views.crear_venta, name='crear_venta'),
    
    path('crear_reserva/', views.crear_reserva, name='crear_reserva'),
    path('mis_reservas/', views.mis_reservas, name='mis_reservas'),
    path('editar_reserva/<int:reserva_id>/', views.editar_reserva, name='editar_reserva'),
    path('eliminar_reserva/<int:reserva_id>/', views.eliminar_reserva, name='eliminar_reserva'),
    path('verificar_disponibilidad_mesa/<int:mesa_id>/', views.verificar_disponibilidad_mesa, name='verificar_disponibilidad_mesa'),
    path('detalle_reserva_ajax/', views.detalle_reserva_ajax, name='detalle_reserva_ajax'),
    path('ajax/toggle_empleado_servicio/', views.ajax_toggle_empleado_servicio, name='ajax_toggle_empleado_servicio'),
    # AJAX admin endpoints used by index_admin
    path('ajax/crear_garzon/', views.ajax_crear_garzon, name='ajax_crear_garzon'),
    path('ajax/editar_garzon/<int:id_usuario>/', views.ajax_editar_garzon, name='ajax_editar_garzon'),
    path('ajax/eliminar_garzon/<int:id_usuario>/', views.ajax_eliminar_garzon, name='ajax_eliminar_garzon'),
    path('ajax/crear_cocinero/', views.ajax_crear_cocinero, name='ajax_crear_cocinero'),
    path('ajax/editar_cocinero/<int:id_usuario>/', views.ajax_editar_cocinero, name='ajax_editar_cocinero'),
    path('ajax/eliminar_cocinero/<int:id_usuario>/', views.ajax_eliminar_cocinero, name='ajax_eliminar_cocinero'),
    path('ajax/crear_mesa/', views.ajax_crear_mesa, name='ajax_crear_mesa'),
    path('ajax/editar_mesa/<int:mesa_id>/', views.ajax_editar_mesa, name='ajax_editar_mesa'),
    path('ajax/eliminar_mesa/<int:mesa_id>/', views.ajax_eliminar_mesa, name='ajax_eliminar_mesa'),
    path('ajax/crear_usuario/', views.ajax_crear_usuario, name='ajax_crear_usuario'),
    path('ajax/editar_usuario/<int:id_usuario>/', views.ajax_editar_usuario, name='ajax_editar_usuario'),
    path('ajax/eliminar_usuario/<int:id_usuario>/', views.ajax_eliminar_usuario, name='ajax_eliminar_usuario'),
    
    path('editar_mesa/<int:mesa_id>/', views.editar_mesa, name='editar_mesa'),
    path('eliminar_mesa/<int:mesa_id>/', views.eliminar_mesa, name='eliminar_mesa'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    path('admin_password/usuario/<int:user_id>/', admin_views.change_usuario_password, name='change_usuario_password'),
    path('admin_password/cliente/<int:cliente_id>/', admin_views.change_cliente_password, name='change_cliente_password'),
    
    path('ajax/crear_menu/', views.crear_menu_cocina, name='ajax_crear_menu'),
    path('ajax/editar_menu_cocina/<int:menu_id>/', views.editar_menu_cocina, name='ajax_editar_menu_cocina'),
    path('ajax/toggle_menu_cocina/<int:menu_id>/', views.ajax_toggle_menu_cocina, name='ajax_toggle_menu_cocina'),
    path('ajax/eliminar_menu_cocina/<int:menu_id>/', views.eliminar_menu_cocina, name='ajax_eliminar_menu_cocina'),
]

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .formulario import LoginForm, UsuarioForm,UploadCSVForm
from .models import usuarios, CalificacionTributaria
import pandas as pd

def login_view(request):
    # Verificar si hay un flag de éxito en la sesión para mostrar el alert
    success = request.session.pop('login_success', False)
    user_nombre = request.session.get('user_nombre', '')
    
    # Si el usuario ya está logueado y no es un redirect de login exitoso, redirigir al home
    if request.session.get('user_id') and not success:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            contrasena = form.cleaned_data['contrasena']
            
            try:
                usuario = usuarios.objects.get(correo=correo)
                
                if usuario.contrasena == contrasena:
                    # Guardar información del usuario en la sesión
                    request.session['user_id'] = str(usuario.id)
                    request.session['user_nombre'] = usuario.nombre
                    request.session['user_correo'] = usuario.correo
                    request.session['user_rol'] = usuario.rol
                    request.session['login_success'] = True
                    
                    # Redirigir al home después de login exitoso
                    return redirect('home')
                else:
                    # Contraseña incorrecta
                    error = "Correo o contraseña incorrectos"
                    return render(request, 'login.html', {
                        'form': form,
                        'error': error
                    })
            except usuarios.DoesNotExist:
                # Usuario no encontrado
                error = "Correo o contraseña incorrectos"
                return render(request, 'login.html', {
                    'form': form,
                    'error': error
                })
            except Exception as e:
                # Error en la consulta
                error = "Error al iniciar sesión. Por favor, intente nuevamente."
                return render(request, 'login.html', {
                    'form': form,
                    'error': error
                })
        else:
            # Formulario inválido
            return render(request, 'login.html', {
                'form': form,
                'error': "Por favor, complete todos los campos correctamente"
            })
    else:
        # GET request - mostrar formulario
        form = LoginForm()
        return render(request, 'login.html', {
            'form': form,
            'success': success,
            'user_nombre': user_nombre
        })

def home_view(request):
    # Verificar que el usuario esté logueado
    if not request.session.get('user_id'):
        return redirect('login')
    
    # Verificar si hay un flag de éxito en la sesión para mostrar el alert
    success = request.session.pop('login_success', False)
    user_nombre = request.session.get('user_nombre', '')
    # Verificar explícitamente si el usuario es administrador (rol == True)
    user_rol = request.session.get('user_rol', False)
    is_admin = bool(user_rol) if user_rol is not None else False
    
    return render(request, 'home.html', {
        'user_nombre': user_nombre,
        'success': success,
        'is_admin': is_admin
    })

def logout_view(request):
    # Limpiar la sesión
    request.session.flush()
    return redirect('login')

def administracion_view(request):
    # Verificar que el usuario esté logueado
    if not request.session.get('user_id'):
        return redirect('login')
    
    # Verificar que el usuario sea administrador
    if not request.session.get('user_rol'):
        return redirect('home')
    
    # Obtener todos los usuarios
    try:
        usuarios_list = usuarios.objects.all()
        total_usuarios = usuarios_list.count()
    except Exception as e:
        usuarios_list = []
        total_usuarios = 0
    
    return render(request, 'administracion.html', {
        'usuarios': usuarios_list,
        'total_usuarios': total_usuarios
    })

def crear_usuario_view(request):
    # Verificar que el usuario esté logueado y sea administrador
    if not request.session.get('user_id') or not request.session.get('user_rol'):
        messages.error(request, 'No autorizado')
        return redirect('administrar')
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo']
            contrasena = form.cleaned_data.get('contrasena')
            rol = form.cleaned_data.get('rol', False)
            ruc = form.cleaned_data.get('ruc', '')
            
            # Validar que la contraseña esté presente al crear
            if not contrasena:
                messages.error(request, 'La contraseña es requerida')
                return render(request, 'crear_usuario.html', {'form': form})
            
            # Verificar si el correo ya existe
            if usuarios.objects(correo=correo).first():
                messages.error(request, 'El correo ya está registrado')
                return render(request, 'crear_usuario.html', {'form': form})
            
            # Crear nuevo usuario
            try:
                nuevo_usuario = usuarios(
                    nombre=nombre,
                    correo=correo,
                    contrasena=contrasena,
                    rol=rol,
                    ruc=ruc
                )
                nuevo_usuario.save()
                messages.success(request, 'Usuario creado exitosamente')
                return redirect('administrar')
            except Exception as e:
                messages.error(request, f'Error al crear usuario: {str(e)}')
        else:
            messages.error(request, 'Por favor, complete todos los campos correctamente')
    else:
        form = UsuarioForm()
    
    return render(request, 'crear_usuario.html', {'form': form})

def modificar_usuario_view(request, usuario_id):
    # Verificar que el usuario esté logueado y sea administrador
    if not request.session.get('user_id') or not request.session.get('user_rol'):
        messages.error(request, 'No autorizado')
        return redirect('administrar')
    
    try:
        usuario = usuarios.objects.get(id=usuario_id)
    except usuarios.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('administrar')
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo']
            contrasena = form.cleaned_data.get('contrasena')
            rol = form.cleaned_data.get('rol', False)
            ruc = form.cleaned_data.get('ruc', '')
            
            # Verificar si el correo ya existe en otro usuario
            usuario_existente = usuarios.objects(correo=correo).first()
            if usuario_existente and str(usuario_existente.id) != usuario_id:
                messages.error(request, 'El correo ya está registrado')
                form = UsuarioForm(initial={
                    'nombre': usuario.nombre,
                    'correo': usuario.correo,
                    'rol': usuario.rol,
                    'ruc': usuario.ruc or ''
                })
                return render(request, 'modificar_usuario.html', {'form': form, 'usuario': usuario})
            
            # Actualizar usuario
            try:
                usuario.nombre = nombre
                usuario.correo = correo
                if contrasena:  # Solo actualizar si se proporciona una nueva contraseña
                    usuario.contrasena = contrasena
                usuario.rol = rol
                usuario.ruc = ruc
                usuario.save()
                messages.success(request, 'Usuario modificado exitosamente')
                return redirect('administrar')
            except Exception as e:
                messages.error(request, f'Error al modificar usuario: {str(e)}')
        else:
            messages.error(request, 'Por favor, complete todos los campos correctamente')
    else:
        form = UsuarioForm(initial={
            'nombre': usuario.nombre,
            'correo': usuario.correo,
            'rol': usuario.rol,
            'ruc': usuario.ruc or ''
        })
    
    return render(request, 'modificar_usuario.html', {'form': form, 'usuario': usuario})

def eliminar_usuario_view(request, usuario_id):
    # Verificar que el usuario esté logueado y sea administrador
    if not request.session.get('user_id') or not request.session.get('user_rol'):
        messages.error(request, 'No autorizado')
        return redirect('administrar')
    
    if request.method == 'POST':
        try:
            usuario = usuarios.objects.get(id=usuario_id)
            
            # No permitir eliminar al propio usuario
            if str(usuario.id) == request.session.get('user_id'):
                messages.error(request, 'No puede eliminar su propia cuenta')
                return redirect('administrar')
            
            usuario.delete()
            messages.success(request, 'Usuario eliminado exitosamente')
            return redirect('administrar')
        except usuarios.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
            return redirect('administrar')
        except Exception as e:
            messages.error(request, f'Error al eliminar usuario: {str(e)}')
            return redirect('administrar')
    
    # GET request - mostrar confirmación
    try:
        usuario = usuarios.objects.get(id=usuario_id)
        return render(request, 'eliminar_usuario.html', {'usuario': usuario})
    except usuarios.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('administrar')


#INGRESAR CALIFCACIONES VIEW
def ingresar_calificacion_view(request):
    factores = range(8, 38)  #basicamente factores es del 8 al 37

    if request.method == "POST": #El POST sirve que para cuando el usuario envia sucede lo siguiente
        data = request.POST

        lista_factores = []#Bueno, se hizo una lista para los factores para no ser redundantes nada mas
        for i in factores:   #En este codigo estamos sacando mediante el for los datos enviados y colocandolo en una
            valor = data.get(f"factor_{i}")
            lista_factores.append(float(valor) if valor else None)
            
        nueva = CalificacionTributaria( # Aqui esta desar
            mercado=data.get("mercado"),
            instrumento=data.get("instrumento"),
            anio=int(data.get("anio")),
            fecha_pago=data.get("fecha_pago"),
            secuencia_evento=int(data.get("secuencia_evento")),
            dividendo=float(data.get("dividendo")),
            valor_historico=float(data.get("valor_historico")),
            descripcion=data.get("descripcion"),
            isfut=data.get("isfut"),
            factor_actualizacion=float(data.get("factor_actualizacion")),
            tipo_sociedad=data.get("tipo_sociedad"),
            corredor=data.get("corredor"),
            factores=lista_factores
        )

        nueva.save()
        return redirect("ingresar_calificaciones")

    return render(request, "ingresar_calificaciones.html", {"factores": factores})
#INGRESAR CALIFICACIONES POR EL CSV MONTOS Y FACTORES 

def validar_factores(df):
    
# aqui use la lógica base original: validar que todas las columnas sean números
    for col in df.columns:
        try:
            df[col].astype(float)
        except:
            return False, f"La columna {col} contiene valores NO numéricos"
    return True,  None


def cargar_factores(request):
    form = UploadCSVForm()

    if request.method == "POST":
        form = UploadCSVForm(request.POST, request.FILES)

        if form.is_valid():
            archivo = request.FILES["archivo"]
            df = pd.read_csv(archivo)

# Use el original con cambio en los factoes, use las columnas heredadas del flujo Streamlit original
            columnas_base = [
                "mercado","instrumento","anio","fecha_pago","secuencia_evento","dividendo",
                "valor_historico","descripcion","isfut","factor_actualizacion","tipo_sociedad","corredor"
            ]
            columnas_factores = [f"factor_{i}" for i in range(8, 38)]

            columnas_requeridas = columnas_base + columnas_factores

#Aqui cambie la validación de columnas (pero es la misma idea del proyecto original, mejorada)
            if list(df.columns) != columnas_requeridas:
                return render(request, "cargar_factores_csv.html", {
                    "form": form,
                    "error": "Las columnas no coinciden con el formato esperado."
                })

#Aqui puse la va validación heredada de Streamlit: factores deben ser numéricos
            factores_df = df[columnas_factores]
            valido, error = validar_factores(factores_df)
            if not valido:
                return render(request, "cargar_factores_csv.html", {"form": form, "error": error})

#Como estamos en django para guardar en MongoDB se usa esta0 versión a diferencia del oorignial
            for _, fila in df.iterrows():
                CalificacionTributaria.objects.create(
                    mercado=fila["mercado"],
                    instrumento=fila["instrumento"],
                    anio=int(fila["anio"]),
                    fecha_pago=fila["fecha_pago"],
                    secuencia_evento=int(fila["secuencia_evento"]),
                    dividendo=float(fila["dividendo"]),
                    valor_historico=float(fila["valor_historico"]),
                    descripcion=fila["descripcion"],
                    isfut=fila["isfut"],
                    factor_actualizacion=float(fila["factor_actualizacion"]),
                    tipo_sociedad=fila["tipo_sociedad"],
                    corredor=fila["corredor"],
                    factores=[float(fila[f"factor_{i}"]) for i in range(8, 38)]
                )

            return render(request, "cargar_factores_csv.html", {
                "form": form,
                "success": "scalificaciones cargadas exitosamente por FACTORES"
            })

    return render(request, "cargar_factores_csv.html", {"form": form})


def cargar_montos(request):
    form = UploadCSVForm()

    if request.method == "POST":
        form = UploadCSVForm(request.POST, request.FILES)

        if form.is_valid():
            archivo = request.FILES["archivo"]
            df = pd.read_csv(archivo)

            columnas_base = [
                "mercado","instrumento","anio","fecha_pago","secuencia_evento","dividendo",
                "valor_historico","descripcion","isfut","factor_actualizacion","tipo_sociedad","corredor"
            ]
            columnas_montos = [f"monto_{i}" for i in range(1, 31)]

            columnas_requeridas = columnas_base + columnas_montos

            if list(df.columns) != columnas_requeridas:
                return render(request, "cargar_montos_csv.html", {
                    "form": form,
                    "error": "Las columnas no coinciden con el formato esperado para montos."
                })

#Esta es la validación numérica (mismo proceso originalpero se aplico a montos)
            montos_df = df[columnas_montos]
            valido, error = validar_factores(montos_df)
            if not valido:
                return render(request, "cargar_montos_csv.html", {"form": form, "error": error})

            for _, fila in df.iterrows():
                valor_hist = float(fila["valor_historico"])

#usamos esta logica para transformar montos a factores
                factores_calculados = [
                    round(float(fila[f"monto_{i}"]) / valor_hist, 6) for i in range(1, 31)
                ]

                CalificacionTributaria.objects.create(
                    mercado=fila["mercado"],
                    instrumento=fila["instrumento"],
                    anio=int(fila["anio"]),
                    fecha_pago=fila["fecha_pago"],
                    secuencia_evento=int(fila["secuencia_evento"]),
                    dividendo=float(fila["dividendo"]),
                    valor_historico=valor_hist,
                    descripcion=fila["descripcion"],
                    isfut=fila["isfut"],
                    factor_actualizacion=float(fila["factor_actualizacion"]),
                    tipo_sociedad=fila["tipo_sociedad"],
                    corredor=fila["corredor"],
                    factores=factores_calculados
                )

            return render(request, "cargar_montos_csv.html", {
                "form": form,
                "success": "Montos cargados y FACTORES ca culados automáticamente"
            })

    return render(request, "cargar_montos_csv.html", {"form": form})

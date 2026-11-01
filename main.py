import os

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(
    title="convenienceIA & dAcliass API",
    description="Plataforma 2 en 1 con motor de notificaciones, asistente dAcliass e integración de pagos con PayPal.",
    version="1.3.0"
)

# ==========================================
# MODELOS DE DATOS (Pydantic)
# ==========================================

class ConsultaCliente(BaseModel):
    texto_usuario: str
    presupuesto_max_usd: float
    latitud: float
    longitud: float
    metodo_transporte: Optional[str] = "caminando"

class ContextoNotificacion(BaseModel):
    usuario_id: str
    latitud: float
    longitud: float
    hora_actual: str
    dia_semana: Optional[str] = "Viernes"
    clima: Optional[str] = "caluroso"

class OfertaRelampago(BaseModel):
    negocio_id: str
    descuento_porcentaje: int
    duracion_minutos: int
    descripcion: str

class SolicituddAcliass(BaseModel):
    negocio_id: str
    mensaje_cliente: str
    accion: Optional[str] = "auto_responder"

class ActualizarPlanNegocio(BaseModel):
    negocio_id: str
    nuevo_plan: str  # "gratis", "pro_dacliass", "patrocinado_top"

# Modelo para recibir la confirmación del pago en PayPal
class ConfirmacionPagoPayPal(BaseModel):
    negocio_id: str
    paypal_order_id: str
    monto: float
    plan_comprado: str  # "pro_dacliass" o "patrocinado_top"

# ==========================================
# RUTAS DE LA APLICACIÓN
# ==========================================

@app.get("/")
def home():
    return {
        "status": "ok", 
        "app": "convenienceIA",
        "message": "Servidor activo con motor de monetización, PayPal, notificaciones y dAcliass."
    }

# ------------------------------------------
# 1. MÓDULO CLIENTE (convenienceIA)
# ------------------------------------------

@app.post("/cliente/asistente-sabores")
def asistente_sabores(consulta: ConsultaCliente):
    """
    IA para clientes: Muestra los locales patrocinados primero y luego los resultados orgánicos.
    """
    return {
        "antojo": consulta.texto_usuario,
        "presupuesto_limite": f"${consulta.presupuesto_max_usd} USD",
        "recomendaciones": [
            {
                "negocio": "Heladería Artesanal VIP",
                "es_patrocinado": True,
                "etiqueta_ads": "Recomendado por convenienceIA 🌟",
                "plato": "Helado de Pistacho Premium",
                "precio_usd": 6.50,
                "calificacion_real": 4.9,
                "ubicacion": "Calle Principal #123",
                "tiempo_llegada": "3 min caminando",
                "estado": "Abierto ahora",
                "oferta_activa": "20% de descuento si llegas en 15 min"
            },
            {
                "negocio": "Café & Postres del Centro",
                "es_patrocinado": False,
                "plato": "Malteada de Chocolate",
                "precio_usd": 5.00,
                "calificacion_real": 4.5,
                "ubicacion": "Av. Central #45",
                "tiempo_llegada": "7 min caminando",
                "estado": "Abierto ahora",
                "oferta_activa": "Sin oferta actual"
            }
        ]
    }

# ------------------------------------------
# 2. MOTOR DE NOTIFICACIONES INTELIGENTES
# ------------------------------------------

@app.post("/cliente/notificaciones/evaluar")
def generar_notificacion_contextual(contexto: ContextoNotificacion):
    notificaciones_generadas = []

    if contexto.hora_actual == "08:00 AM":
        notificaciones_generadas.append({
            "tipo": "Antojo Mañanero ☕",
            "titulo": "¡Buenos días!",
            "mensaje": "Sé que te acaba de costar levantarte... y creo que necesitas probar un café recién hecho de Café Central a solo 2 minutos de ti ☕. ¡Pasa por tu descuento de la mañana!"
        })
    elif contexto.hora_actual == "02:00 PM" and contexto.clima == "caluroso":
        notificaciones_generadas.append({
            "tipo": "Antojo Tarde Calurosa 🍦",
            "titulo": "¡Hora de refrescarse!",
            "mensaje": "¿Viste el nuevo sabor de Helados Bon? 🍦 Tienen una promo relámpago de 2x1 solo por las próximas 2 horas. Pásate antes de que se acabe."
        })

    if contexto.hora_actual == "07:30 PM" and contexto.dia_semana == "Viernes":
        notificaciones_generadas.append({
            "tipo": "Combo de Viernes 🍔",
            "titulo": "¡Noche de Viernes!",
            "mensaje": "¿Viste el nuevo combo familiar que sacó KFC / McDonald's hoy? 🍔🍟 Te dejamos la ruta más rápida sin tráfico y un cupón de 15% de descuento en la app."
        })

    notificaciones_generadas.append({
        "tipo": "Geolocalización / Cercanía 📍",
        "titulo": "¡Cerca de ti!",
        "mensaje": "Estás a 50 metros de Barbería & Co. Tienen espacio libre justo ahora y 20% de descuento si entras en los próximos 10 minutos."
    })

    return {
        "usuario_id": contexto.usuario_id,
        "notificaciones_activas": notificaciones_generadas
    }

# ------------------------------------------
# 3. MÓDULO DUEÑO (dAcliass) & MONETIZACIÓN CON PAYPAL
# ------------------------------------------

@app.post("/dacliass/monetizacion/cambiar-plan")
def cambiar_plan_negocio(datos_plan: ActualizarPlanNegocio):
    precios = {
        "gratis": "$0 USD/mes (Funciones básicas)",
        "pro_dacliass": "$29 USD/mes (Asistente IA + Ofertas Relámpago Ilimitadas)",
        "patrocinado_top": "$59 USD/mes (Asistente IA + Primeros lugares en IA y Push)"
    }
    return {
        "negocio_id": datos_plan.negocio_id,
        "plan_activado": datos_plan.nuevo_plan,
        "detalle_cobro": precios.get(datos_plan.nuevo_plan, "Plan no válido"),
        "status": "Suscripción actualizada correctamente"
    }

@app.post("/dacliass/monetizacion/confirmar-paypal")
def confirmar_pago_paypal(pago: ConfirmacionPagoPayPal):
    """
    Ruta para recibir la confirmación de que un cliente/negocio realizó su pago por PayPal.
    """
    return {
        "status": "pago_recibido",
        "mensaje": f"El pago de ${pago.monto} USD enviado por PayPal fue procesado correctamente y depositado a tu cuenta.",
        "negocio_id": pago.negocio_id,
        "plan_activo": pago.plan_comprado,
        "transaccion_id": pago.paypal_order_id
    }

@app.post("/dacliass/oferta-relampago")
def publicar_oferta_relampago(oferta: OfertaRelampago):
    return {
        "status": "oferta_publicada",
        "mensaje": f"¡Oferta relámpago activada! {oferta.descuento_porcentaje}% de descuento en el negocio {oferta.negocio_id} durante {oferta.duracion_minutos} minutos."
    }

@app.post("/dacliass/atencion-cliente")
def asistente_dueno_dacliass(solicitud: SolicituddAcliass):
    respuesta_generada = f"¡Hola! Sí, tenemos esa opción disponible en nuestro menú y estamos abiertos hasta las 11:00 PM."
    return {
        "negocio_id": solicitud.negocio_id,
        "asistente": "dAcliass AI",
        "respuesta_sugerida": respuesta_generada,
        "estado": "Respuesta enviada al cliente"
    }



from fastapi.responses import HTMLResponse
import os

@app.get("/", include_in_schema=False)
def servir_frontend():
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_archivo = os.path.join(ruta_actual, "index.html")
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)




    

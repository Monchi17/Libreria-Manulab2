
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon

ESPESOR=41
ALTURA_VIGA=2440
ALTURA_VENTANA=936+41*2

TIPOS_VENTANA=("V1","V2","V3","V4")

piezas_Muros_Altillos=[]


def guardar_pieza(tipo,x,y,ancho,alto,largo,h_izq,h_der,posicion=None,orientacion=None):
    piezas_Muros_Altillos.append({"id":len(piezas_Muros_Altillos)+1,"tipo":tipo,"muro":{"largo":largo,"alto_izq":h_izq,"alto_der":h_der},"coordenadas":{"x":x,"y":y},"dimensiones":{"ancho":ancho,"alto":alto},"espesor":ESPESOR,"posicion":posicion,"orientacion":orientacion})


def obtener_abertura(largo,abertura):
    if len(abertura)==4:
        ancho,alto,desplazamiento,tipo=abertura
    else:
        ancho,alto,tipo=abertura
        desplazamiento=0

    centro=largo/2+desplazamiento
    x0=centro-ancho/2
    x1=centro+ancho/2
    y0=ALTURA_VENTANA if tipo in TIPOS_VENTANA else 0
    y1=y0+alto

    return x0,x1,y0,y1,tipo


def dibujar_refuerzo(ax,x,y,ancho,alto,largo,h_izq,h_der,tipo):
    if ancho<=0 or alto<=0: return

    ax.add_patch(Rectangle((x,y),ancho,alto,linewidth=.8,edgecolor="black",facecolor="lightgray"))
    guardar_pieza(tipo,x,y,ancho,alto,largo,h_izq,h_der)


def dibujar_viga_segmentada(ax,largo,h_izq,h_der,viga,piezas_actuales):
    y=viga-ESPESOR
    intervalos=[]

    for pieza in piezas_actuales:
        ancho=pieza["dimensiones"]["ancho"]
        alto=pieza["dimensiones"]["alto"]
        x=pieza["coordenadas"]["x"]
        py=pieza["coordenadas"]["y"]

        if ancho>=alto: continue

        if py<=viga and py+alto>=y:
            x0=max(0,x)
            x1=min(largo,x+ancho)
            if x1>x0: intervalos.append((x0,x1))

    intervalos.sort()
    unidos=[]

    for x0,x1 in intervalos:
        if unidos and x0<=unidos[-1][1]+0.001:
            unidos[-1]=(unidos[-1][0],max(unidos[-1][1],x1))
        else:
            unidos.append((x0,x1))

    inicio=0

    for x0,x1 in unidos:
        if x0>inicio:
            dibujar_refuerzo(ax,inicio,y,x0-inicio,ESPESOR,largo,h_izq,h_der,"viga_horizontal")
        inicio=max(inicio,x1)

    if inicio<largo:
        dibujar_refuerzo(ax,inicio,y,largo-inicio,ESPESOR,largo,h_izq,h_der,"viga_horizontal")


def dibujar_muro_altillo(ax,largo,h_izq,h_der,viga=ALTURA_VIGA,pies=None,aberturas=None,tiene_ventana_altillo=False,desplazamiento_altillo=0):
    inicio_piezas=len(piezas_Muros_Altillos)

    if pies is None: pies=[]
    if aberturas is None: aberturas=[]

    aberturas_calc=[obtener_abertura(largo,a) for a in aberturas]

    dibujar_refuerzo(ax,0,0,largo,ESPESOR,largo,h_izq,h_der,"solera_inferior")

    dh=h_der-h_izq
    L=(largo**2+dh**2)**.5
    nx=-dh/L
    ny=largo/L

    puntos=[(0,h_izq),(largo,h_der),(largo+nx*ESPESOR,h_der+ny*ESPESOR),(nx*ESPESOR,h_izq+ny*ESPESOR)]

    ax.add_patch(Polygon(puntos,closed=True,linewidth=.8,edgecolor="black",facecolor="lightgray"))

    guardar_pieza("solera_inclinada",0,h_izq,largo,ESPESOR,largo,h_izq,h_der,"superior","inclinada")

    dibujar_refuerzo(ax,0,ESPESOR,ESPESOR,h_izq-ESPESOR,largo,h_izq,h_der,"pie_extremo")
    dibujar_refuerzo(ax,largo-ESPESOR,ESPESOR,ESPESOR,h_der-ESPESOR,largo,h_izq,h_der,"pie_extremo")

    abertura_superior=None

    if tiene_ventana_altillo:
        ancho,alto,desplazamiento=ventana_altillo
        centro=largo/2+desplazamiento
        xa=centro-ancho/2
        xb=centro+ancho/2
        yc=h_izq+(h_der-h_izq)*(centro/largo)-ESPESOR
        abertura_superior=(xa,xb,yc-alto,yc)

    pies_finales=sorted(set(round(x,6) for x in pies if ESPESOR<x<largo-ESPESOR))

    for x in pies_finales:
        altura=h_izq+(h_der-h_izq)*(x/largo)
        tramos=[(ESPESOR,altura)]
        cortes=[(x0,x1,y0,y1) for x0,x1,y0,y1,t in aberturas_calc]

        if abertura_superior: cortes.append(abertura_superior)

        for x0,x1,y0,y1 in cortes:
            if x-ESPESOR<x1 and x+ESPESOR>x0:
                nuevos=[]

                for ya,yb in tramos:
                    if y0>ya: nuevos.append((ya,min(y0,yb)))
                    if y1<yb: nuevos.append((max(y1,ya),yb))

                tramos=[(a,b) for a,b in nuevos if b>a]

        for ya,yb in tramos:
            dibujar_refuerzo(ax,x,ya,ESPESOR,yb-ya,largo,h_izq,h_der,"pie_interior")

    # REFUERZOS DE ABERTURAS
    for x0,x1,y0,y1,tipo in aberturas_calc:

        for x,lado in [(x0-ESPESOR,"izquierdo"),(x0,"izquierdo")]:
            altura=h_izq+(h_der-h_izq)*(x/largo)

            if tiene_ventana_altillo and desplazamiento_altillo<0:
                altura=min(altura,viga)

            nombre="refuerzo_ventana_lateral" if tipo in TIPOS_VENTANA else "refuerzo_puerta_lateral"

            dibujar_refuerzo(ax,x,ESPESOR,ESPESOR,altura-ESPESOR,largo,h_izq,h_der,nombre)

        if tipo in TIPOS_VENTANA and round(x1-x0)==1200:
            refuerzos_derechos=[x1-ESPESOR,x1,x1+ESPESOR]
        else:
            refuerzos_derechos=[x1,x1+ESPESOR]

        for x in refuerzos_derechos:
            altura=h_izq+(h_der-h_izq)*(x/largo)

            if tiene_ventana_altillo and desplazamiento_altillo>0:
                altura=min(altura,viga)

            nombre="refuerzo_ventana_lateral" if tipo in TIPOS_VENTANA else "refuerzo_puerta_lateral"

            if tipo in TIPOS_VENTANA and round(x1-x0)==1200 and abs(x-(x1-ESPESOR))<0.001:
                dibujar_refuerzo(ax,x,0,ESPESOR,ALTURA_VENTANA,largo,h_izq,h_der,nombre)
                dibujar_refuerzo(ax,x,ALTURA_VENTANA+700,ESPESOR,altura-(ALTURA_VENTANA+700),largo,h_izq,h_der,nombre)
            else:
                dibujar_refuerzo(ax,x,ESPESOR,ESPESOR,altura-ESPESOR,largo,h_izq,h_der,nombre)

        if tipo in TIPOS_VENTANA:
            if round(x1-x0)==500 and not (tiene_ventana_altillo and desplazamiento_altillo<0):
                dibujar_refuerzo(ax,x1-ESPESOR,ESPESOR,ESPESOR,1000-ESPESOR,largo,h_izq,h_der,"refuerzo_adicional")

            dibujar_refuerzo(ax,x0,y0-ESPESOR,x1-x0,ESPESOR,largo,h_izq,h_der,"refuerzo_ventana_inferior")
            dibujar_refuerzo(ax,x0,y1,x1-x0+ESPESOR,ESPESOR,largo,h_izq,h_der,"refuerzo_ventana_superior")
            dibujar_refuerzo(ax,x0,y1-ESPESOR,x1-x0+ESPESOR,ESPESOR,largo,h_izq,h_der,"refuerzo_ventana_superior_interior")

        else:
            dibujar_refuerzo(ax,x0,y1,x1-x0,ESPESOR,largo,h_izq,h_der,"refuerzo_puerta_superior")

    piezas_actuales=piezas_Muros_Altillos[inicio_piezas:]
    dibujar_viga_segmentada(ax,largo,h_izq,h_der,viga,piezas_actuales)

    return aberturas_calc


def dibujar_ventana_altillo(ax,largo,h_izq,h_der):
    ancho,alto,desplazamiento=ventana_altillo

    centro=largo/2+desplazamiento
    x0=centro-ancho/2
    x1=centro+ancho/2

    altura_centro=h_izq+(h_der-h_izq)*(centro/largo)
    y1=altura_centro-ESPESOR
    y0=y1-alto

    dibujar_refuerzo(ax,x0-ESPESOR,y0,ESPESOR,alto,largo,h_izq,h_der,"marco_ventana_altillo_izquierdo")
    dibujar_refuerzo(ax,x1,y0,ESPESOR,alto,largo,h_izq,h_der,"marco_ventana_altillo_derecho")

    if desplazamiento<0:
        dibujar_refuerzo(ax,ESPESOR,y0,1200,ESPESOR,largo,h_izq,h_der,"refuerzo_ventana_altillo_inferior")
    else:
        dibujar_refuerzo(ax,1200,y0,1200,ESPESOR,largo,h_izq,h_der,"refuerzo_ventana_altillo_inferior")

    dibujar_refuerzo(ax,x0-ESPESOR,y1,ancho+ESPESOR*2,ESPESOR,largo,h_izq,h_der,"marco_ventana_altillo_superior")
    dibujar_refuerzo(ax,x0-2*ESPESOR,y0,ESPESOR,alto+ESPESOR,largo,h_izq,h_der,"refuerzo_ventana_altillo_izquierdo")
    dibujar_refuerzo(ax,x1+ESPESOR,y0+ESPESOR,ESPESOR,alto,largo,h_izq,h_der,"refuerzo_ventana_altillo_derecho")


def dibujar_esquinas_L(ax,largo,h_izq,h_der,e,color="black",lw=1.5):
    L=e*2
    dh=h_der-h_izq
    largo_inclinado=(largo**2+dh**2)**0.5

    ux=largo/largo_inclinado
    uy=dh/largo_inclinado

    esquinas=[(0,0,1,1,0),(largo,0,-1,1,0),(0,h_izq+ESPESOR,1,-1,1),(largo,h_der+ESPESOR,-1,-1,1)]

    for x,y,dx,dy,superior in esquinas:
        if superior:
            vx=ux*dx
            vy=uy*dx
            px=-uy*dy
            py=ux*dy
        else:
            vx=dx
            vy=0
            px=0
            py=dy

        ax.plot([x,x+vx*L],[y,y+vy*L],color=color,lw=lw,zorder=10)
        ax.plot([x,x+px*L],[y,y+py*L],color=color,lw=lw,zorder=10)


def plot_muros_altillos(muros):
    piezas_Muros_Altillos.clear()
    figuras=[]

    for i,muro in enumerate(muros,1):
        largo,h_izq,h_der=muro[:3]
        viga=ALTURA_VIGA
        pies=[]
        aberturas=[]
        tiene_ventana_altillo=False

        if len(muro)>3:
            for elemento in muro[3:]:
                if isinstance(elemento,str) and elemento=="V":
                    tiene_ventana_altillo=True

            if isinstance(muro[3],list):
                pies=muro[3]
            else:
                viga=muro[3]

                if len(muro)>4 and isinstance(muro[4],list):
                    pies=muro[4]

                if len(muro)>5:
                    aberturas=muro[5:]

        if len(muro)>3 and isinstance(muro[3],tuple):
            aberturas.append(muro[3])

        if len(muro)>4 and isinstance(muro[4],tuple):
            aberturas.append(muro[4])

        if len(muro)>5:
            aberturas.extend(x for x in muro[5:] if isinstance(x,tuple))

        fig,ax=plt.subplots(figsize=(4,2.5))
        dibujar_muro_altillo(ax,largo,h_izq,h_der,viga,pies,aberturas,tiene_ventana_altillo,ventana_altillo[2])

        if tiene_ventana_altillo:
            dibujar_ventana_altillo(ax,largo,h_izq,h_der)

        dibujar_esquinas_L(ax,largo,h_izq,h_der,ESPESOR)

        ax.set_xlim(-150,largo+150)
        ax.set_ylim(-150,max(h_izq,h_der,viga)+300)
        ax.set_aspect("equal",adjustable="box")
        ax.grid(alpha=.3)
        ax.set_title(f"MURO {i}",fontsize=4)
        ax.tick_params(axis="both",labelsize=3)

        plt.tight_layout()
        figuras.append(fig)

    return figuras


# CONFIGURACIÓN DE VENTANAS Y PUERTAS

V1=(910,500,100,"V1")
V2=(910,500,-120,"V2")
V3=(1200,700,20,"V3")
P1=(762,2009,400,"P")
V4=(500,600,-320,"V4")

ventana_altillo=[910,583,515]


# DATOS DE LA LIBRERÍA 02

MUROS_LIB_02 = [
    [2440,3071,3071,[600,1200,1799],V2,"V"],
    [2440,3071,3071,[600,1200],V3,"V"],
    [2440,2775,2775,[600,1200,1799],P1],
    [2440,3071,2775,[42,1799,2440-82],V4],
    [2440,2775,2775,[600,1200],V3],
    [2440,2715,3071,[600,1200],V3],
    [500,2728,2792],
    [200,3105,3131],
    [1002,2775,2775,[600]],
    [2440,2728,3071,[620-ESPESOR,1200-41,1799-41]]
]


# INTERFAZ PRINCIPAL

st.set_page_config(
    page_title="Librería Manulab",
    page_icon="🏗️",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .subtitle {
        text-align: center;
        color: #8a8a8a;
        font-size: 16px;
        margin-bottom: 28px;
    }
    div.stButton > button {
        width: 100%;
        height: 58px;
        font-size: 18px;
        font-weight: 700;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-title">LIBRERÍA MANULAB</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Biblioteca de componentes y estructuras de muros</div>',
    unsafe_allow_html=True
)

if "libreria_seleccionada" not in st.session_state:
    st.session_state.libreria_seleccionada = None

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("LIB 00", key="lib00"):
        st.session_state.libreria_seleccionada = "LIB 00"

with col2:
    if st.button("LIB 01", key="lib01"):
        st.session_state.libreria_seleccionada = "LIB 01"

with col3:
    if st.button("LIB 02", key="lib02"):
        st.session_state.libreria_seleccionada = "LIB 02"

st.divider()

if st.session_state.libreria_seleccionada == "LIB 01":
    st.subheader("LIBRERÍA 01")
    st.info("Esta librería estará disponible próximamente.")

elif st.session_state.libreria_seleccionada == "LIB 00":
    st.subheader("LIBRERÍA 00")
    st.caption("Refugio")

    figuras = plot_muros_altillos(MUROS_LIB_02)

    for i, figura in enumerate(figuras, start=1):
        st.pyplot(figura, use_container_width=False)
        plt.close(figura)

elif st.session_state.libreria_seleccionada == "LIB 03":
    st.subheader("LIBRERÍA 03")
    st.info("Esta librería estará disponible próximamente.")

else:
    st.info("Selecciona una librería para visualizar su contenido.")

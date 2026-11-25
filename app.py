
import os
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon,Circle

ESPESOR=41
DIAMETRO_PUNTO=4
RADIO_PUNTO=DIAMETRO_PUNTO/2
LARGO_ESCUADRA=100
ALTURA_VIGA=2440
ALTURA_VENTANA=936+41*2
TIPOS_VENTANA=("V1","V2","V3","V4")

LARGO_MURO=2400
MARGEN_SUPERIOR=300
ALTURA_MURO_CIEGO=2318

MUROS=[("V2",1500,1200,1200,0),("V1",1350,500,800,280),("V1",1350,500,800,-280),("P3",1350,832,2025,-109),("P1",1200,900,2025,0),("P2",1500,900,2025,-109)]

MUROS_CIEGOS=[(600,[],250*3+450+750+900),(900,[580],250*2+450+750),(750,[580],250+450),(450,[],0)]
MUROS_CIEGOS_2=[(1500,[580,1180],0),(1200,[600],1500+250),(1200,[580],1500+250)]

ALTILLOS=[("F1",954,3641,[600,600,600,600,600]),("F2",300,3641,[600,600,600,600,600]),("F3",630,3641,[600,600,600,600,600])]

FRONTONES_TRIANGULARES=[("F1",3300,1278,802,[213,540,579,559,559]),("F2",2400,882,594,[559,559,559]),("F3",3750,594,144,[489,630,559,579,691,448])]

TECHUMBRES=[
(1200,2740,[518+ESPESOR,518+ESPESOR*2],[1138+ESPESOR,1138+ESPESOR*2+300],[1200,1540]),
(1200,3150,[518+ESPESOR,518+ESPESOR*2],[1138+ESPESOR,1138+ESPESOR*2+710],[1200,1950]),
(900,2740,[368+ESPESOR,368+ESPESOR*2],[1138+ESPESOR,1138+ESPESOR*2+300],[1200,1540]),
(900,3150,[368+ESPESOR,368+ESPESOR*2],[1159+ESPESOR,1159+ESPESOR+689],[1200,1200+ESPESOR+709])
]

ENTREPISOS=[
(750,2850,[314+ESPESOR],[1138+ESPESOR,1138+ESPESOR+389],[ESPESOR+1159,ESPESOR+1159+ESPESOR+385]),
(1200,2850,[359+ESPESOR,359*2+ESPESOR*2],[1138+ESPESOR,1609],[ESPESOR+1159,ESPESOR+1159+ESPESOR+389],[1138+ESPESOR,1609]),
(1200,1950,[359+ESPESOR,359*2+ESPESOR*2],[1138+ESPESOR],[1155+ESPESOR],[1138+ESPESOR]),
(900,2850,[359+ESPESOR,359*2+ESPESOR*2],[1138+ESPESOR,1138+ESPESOR+389+ESPESOR],[ESPESOR+1159,ESPESOR+1159+ESPESOR+389],[]),
(750,2700,[359+ESPESOR],[1138+ESPESOR,ESPESOR+1138+ESPESOR+259],[ESPESOR+1159,ESPESOR+1159+ESPESOR+259]),
(750,1800,[359+ESPESOR],[ESPESOR+1138],[ESPESOR+1159],[])
]

def configurar_ejes(ax,ancho,alto,margen=100):
    ax.set_xlim(-margen,ancho+margen)
    ax.set_ylim(-margen,alto+margen)
    ax.set_aspect("equal",adjustable="box")
    ax.set_xlabel("Ancho (mm)")
    ax.set_ylabel("Alto (mm)")
    ax.grid(True,linestyle="--",alpha=.35)

def crear_figura(titulo,ancho,alto,margen=100,tamano=(9,5)):
    fig,ax=plt.subplots(figsize=tamano)
    ax.set_title(titulo)
    configurar_ejes(ax,ancho,alto,margen)
    return fig,ax

def dibujar_rectangulo(ax,x,y,ancho,alto,color="black",lw=.8):
    ax.add_patch(Rectangle((x,y),ancho,alto,fill=False,edgecolor=color,linewidth=lw))

def dibujar_rect_lineas(ax,x,y,ancho,largo,lw=.7,color="black",relleno=None):
    ax.add_patch(Rectangle((x,y),ancho,largo,fill=bool(relleno),edgecolor=color,facecolor=relleno if relleno else "none",linewidth=lw))

def posicion_abertura(ancho_muro,largo_muro,ancho_ab,largo_ab,margen_superior,desplazamiento=0):
    return (ancho_muro-ancho_ab)/2+desplazamiento,largo_muro-margen_superior-largo_ab

def crear_muros_con_aberturas(modelos,largo_muro,margen_superior):
    muros=[]
    for nombre,ancho_muro,ancho_ab,alto_ab,desplazamiento in modelos:
        x,y=posicion_abertura(ancho_muro,largo_muro,ancho_ab,alto_ab,margen_superior,desplazamiento)
        tipo="Puerta" if nombre.startswith("P") else "Ventana"
        muros.append({"nombre":nombre,"tipo":tipo,"muro":(ancho_muro,largo_muro),"abertura":(ancho_ab,alto_ab),"posicion":(x,y)})
    return muros

def piezas_marco_ventana(x,y,ancho,alto,e):
    return [(x-e,y+alto,ancho+2*e,e),(x-e,y-e,ancho+2*e,e),(x-e,y,e,alto),(x+ancho,y,e,alto)]

def piezas_marco_puerta(x,y,ancho,alto,e):
    return [(x-e,y+alto,ancho+2*e,e),(x-e,y,e,alto),(x+ancho,y,e,alto)]

def generar_figuras_muros_aberturas():
    figuras=[]
    muros=crear_muros_con_aberturas(MUROS,LARGO_MURO,MARGEN_SUPERIOR)
    for i,m in enumerate(muros):
        ancho_muro,largo_muro=m["muro"]
        w,h=m["abertura"]
        x,y=m["posicion"]
        fig,ax=plt.subplots(figsize=(5,6))
        ax.set_title(f'{m["nombre"]} - {ancho_muro} mm')
        dibujar_rect_lineas(ax,0,0,ancho_muro,largo_muro)
        dibujar_rect_lineas(ax,x,y,w,h)
        piezas=piezas_marco_ventana(x,y,w,h,ESPESOR) if m["tipo"]=="Ventana" else piezas_marco_puerta(x,y,w,h,ESPESOR)
        for pieza in piezas:
            dibujar_rect_lineas(ax,*pieza)
        dibujar_rect_lineas(ax,0,largo_muro-ESPESOR,ancho_muro,ESPESOR)
        dibujar_rect_lineas(ax,0,0,ancho_muro,ESPESOR)
        centro=x+w/2
        x_centro=centro-ESPESOR/2
        y_inicio=y+h
        altura=largo_muro-y_inicio
        if altura>0:
            dibujar_rect_lineas(ax,x_centro,y_inicio,ESPESOR,altura)
        dibujar_rect_lineas(ax,0,0,ESPESOR,largo_muro)
        dibujar_rect_lineas(ax,ancho_muro-ESPESOR,0,ESPESOR,largo_muro)
        for px in (x-2*ESPESOR,x-ESPESOR,x+w,x+w+ESPESOR):
            if 0<=px<=ancho_muro-ESPESOR:
                dibujar_rect_lineas(ax,px,0,ESPESOR,largo_muro)
        ax.set_xlim(-100,ancho_muro+100)
        ax.set_ylim(-100,largo_muro+100)
        ax.set_aspect("equal")
        ax.set_xlabel("Ancho (mm)")
        ax.set_ylabel("Alto (mm)")
        ax.grid(True,alpha=.25)
        figuras.append(fig)
    return figuras

def dibujar_muro_ciego(ax,ancho,pies):
    e=ESPESOR
    alto=ALTURA_MURO_CIEGO
    dibujar_rectangulo(ax,0,0,ancho,alto)
    dibujar_rectangulo(ax,0,0,e,alto)
    dibujar_rectangulo(ax,ancho-e,0,e,alto)
    dibujar_rectangulo(ax,0,0,ancho,e)
    dibujar_rectangulo(ax,0,alto-e,ancho,e)
    for x in pies:
        if e<x<ancho-e:
            dibujar_rectangulo(ax,x,e,e,alto-2*e)

def generar_figuras_muros_ciegos(muros,grupo):
    figuras=[]
    for i,(ancho,pies,_) in enumerate(muros):
        fig,ax=crear_figura(f"Muro ciego {grupo} - {i+1}",ancho,ALTURA_MURO_CIEGO,100,(6,7))
        dibujar_muro_ciego(ax,ancho,pies)
        figuras.append(fig)
    return figuras

def convertir_letra(n):
    letra=""
    while n>=0:
        letra=chr(n%26+65)+letra
        n=n//26-1
    return letra

def agregar_punto(ax,x,y,puntos,r=RADIO_PUNTO):
    ax.add_patch(Circle((x,y),r,color="red",zorder=5))
    puntos.append((x,y))

def dibujar_puntos_palos(ax,x0,y0,alto,largo,posiciones,e=ESPESOR):
    r=RADIO_PUNTO
    puntos=[]
    posiciones=sorted(set(posiciones))
    for i,p in enumerate(posiciones):
        izquierda=abs(p)<=1e-6
        derecha=abs(p-(largo-e))<=1e-6
        if not derecha:
            py=y0+alto-e-r
            if i>=len(posiciones)-2:
                py=y0+alto-ESPESOR*2
            agregar_punto(ax,x0+p+e+r*2,py-r*2,puntos,r)
        if not izquierda:
            py=y0+e+r
            if i==1:
                py=y0+ESPESOR*2
            agregar_punto(ax,x0+p-r*2,py+r*2,puntos,r)
        if izquierda:
            agregar_punto(ax,x0+p+e+r*2,y0+ESPESOR*2+r*2,puntos,r)
    agregar_punto(ax,x0+largo-ESPESOR-r*2,y0+alto-ESPESOR*2-r*2,puntos,r)
    return puntos

def dibujar_esquinas_L_componentes(ax,x0,y0,largo,alto,largo_L=LARGO_ESCUADRA,lw=1.5):
    esquinas=[(x0,y0,1,1),(x0+largo,y0,-1,1),(x0,y0+alto,1,-1),(x0+largo,y0+alto,-1,-1)]
    for x,y,dx,dy in esquinas:
        ax.plot([x,x+dx*largo_L],[y,y],color="blue",lw=lw,zorder=6)
        ax.plot([x,x],[y,y+dy*largo_L],color="blue",lw=lw,zorder=6)

def dibujar_letras_puntos(ax,puntos,letra_inicial=0):
    for i,(x,y) in enumerate(puntos):
        ax.annotate(convertir_letra(letra_inicial+i),(x,y),xytext=(3,2),textcoords="offset points",fontsize=6,color="darkred",fontweight="bold",zorder=8)

def dibujar_altillo_componentes(ax,alto,largo,espaciamientos):
    e=ESPESOR
    posiciones=[0]
    acumulado=0
    for distancia in espaciamientos:
        acumulado+=distancia
        posiciones.append(acumulado)
    posiciones.append(largo-e)
    posiciones=sorted(set(p for p in posiciones if 0<=p and p+e<=largo))
    piezas=[(0,0,largo,e),(0,alto-e,largo,e),(e,e,559,e),(largo-600,alto-2*e,559,e)]+[(p,0,e,alto) for p in posiciones]
    for x,y,w,h in piezas:
        dibujar_rectangulo(ax,x,y,w,h)
    puntos=dibujar_puntos_palos(ax,0,0,alto,largo,posiciones)
    dibujar_esquinas_L_componentes(ax,0,0,largo,alto)
    dibujar_letras_puntos(ax,puntos)
    
def generar_figuras_altillos_componentes():
    figuras=[]
    for nombre,alto,largo,espaciamientos in ALTILLOS:
        fig,ax=crear_figura(f"Altillo {nombre}",largo,alto,120)
        dibujar_altillo_componentes(ax,alto,largo,espaciamientos)
        figuras.append(fig)
    return figuras

def calcular_posiciones_palos(largo,espaciamientos):
    posiciones=[0]
    acumulado=0
    for distancia in espaciamientos:
        acumulado+=ESPESOR+distancia
        posiciones.append(acumulado)
    posicion_final=largo-ESPESOR
    if posiciones[-1]<posicion_final:
        posiciones.append(posicion_final)
    elif posiciones[-1]>posicion_final:
        posiciones=[p for p in posiciones if p<=posicion_final]
        posiciones.append(posicion_final)
    return sorted(set(posiciones))

def dibujar_fronton_triangular(ax,largo,alto_mayor,alto_menor,espaciamientos):
    e=ESPESOR
    pendiente=(alto_mayor-alto_menor)/largo
    dibujar_rectangulo(ax,0,0,largo,e)
    puntos_superior=[(0,alto_mayor),(largo,alto_menor),(largo,alto_menor-e),(0,alto_mayor-e)]
    ax.add_patch(Polygon(puntos_superior,closed=True,fill=False,edgecolor="black",linewidth=.8))
    for x in calcular_posiciones_palos(largo,espaciamientos):
        if 0<=x and x+e<=largo:
            altura=alto_mayor-pendiente*(x+e/2)
            dibujar_rectangulo(ax,x,e,e,max(0,altura-e))

def generar_figuras_frontones():
    figuras=[]
    for nombre,largo,alto_mayor,alto_menor,espaciamientos in FRONTONES_TRIANGULARES:
        fig,ax=crear_figura(f"Frontón triangular {nombre}",largo,alto_mayor,alto_menor+120,(9,5))
        dibujar_fronton_triangular(ax,largo,alto_mayor,alto_menor,espaciamientos)
        figuras.append(fig)
    return figuras

def dibujar_techumbre(ax,ancho,largo,pies,piezas_izquierdas,piezas_derechas):
    e=ESPESOR
    dibujar_rectangulo(ax,0,0,ancho,largo)
    dibujar_rectangulo(ax,0,0,ancho,e)
    dibujar_rectangulo(ax,0,largo-e,ancho,e)
    dibujar_rectangulo(ax,0,0,e,largo)
    dibujar_rectangulo(ax,ancho-e,0,e,largo)
    for x in pies:
        if e<x<ancho-e:
            dibujar_rectangulo(ax,x,e,e,largo-2*e)
    for y in piezas_izquierdas:
        if 0<=y and y+e<=largo:
            largo_pieza=max(0,pies[0]-e) if pies else ancho-2*e
            if largo_pieza>0:
                dibujar_rectangulo(ax,e,y,largo_pieza,e)
    for y in piezas_derechas:
        if 0<=y and y+e<=largo:
            inicio=pies[-1]+e if pies else e
            largo_pieza=max(0,ancho-e-inicio)
            if largo_pieza>0:
                dibujar_rectangulo(ax,inicio,y,largo_pieza,e)

def generar_figuras_techumbres():
    figuras=[]
    for i,(ancho,largo,pies,izquierdas,derechas) in enumerate(TECHUMBRES):
        fig,ax=crear_figura(f"Techumbre {i+1}",ancho,largo,100)
        dibujar_techumbre(ax,ancho,largo,pies,izquierdas,derechas)
        figuras.append(fig)
    return figuras

def dibujar_entrepiso(ax,ancho,largo,pies,espacios):
    e=ESPESOR
    dibujar_rectangulo(ax,0,0,ancho,largo)
    dibujar_rectangulo(ax,0,0,ancho,e)
    dibujar_rectangulo(ax,0,largo-e,ancho,e)
    dibujar_rectangulo(ax,0,0,e,largo)
    dibujar_rectangulo(ax,ancho-e,0,e,largo)
    pies_validos=[x for x in pies if e<x<ancho-e]
    for x in pies_validos:
        dibujar_rectangulo(ax,x,e,e,largo-2*e)
    limites=sorted(set([e]+pies_validos+[ancho-e]))
    for i,posiciones in enumerate(espacios):
        if i>=len(limites)-1:
            break
        x_inicio=limites[i]
        ancho_pieza=limites[i+1]-x_inicio
        for y in posiciones:
            if 0<=y and y+e<=largo:
                dibujar_rectangulo(ax,x_inicio,y,ancho_pieza,e)

def generar_figuras_entrepisos():
    figuras=[]
    for i,(ancho,largo,pies,*espacios) in enumerate(ENTREPISOS):
        fig,ax=crear_figura(f"Entrepiso {i+1}",ancho,largo,100)
        dibujar_entrepiso(ax,ancho,largo,pies,espacios)
        figuras.append(fig)
    return figuras


# LIBRERIA 02: MUROS Y ALTILLOS

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
    if ancho<=0 or alto<=0:
        return
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
        if ancho>=alto:
            continue
        if py<=viga and py+alto>=y:
            x0=max(0,x)
            x1=min(largo,x+ancho)
            if x1>x0:
                intervalos.append((x0,x1))
    intervalos.sort()
    unidos=[]
    for x0,x1 in intervalos:
        if unidos and x0<=unidos[-1][1]+.001:
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
    if pies is None:
        pies=[]
    if aberturas is None:
        aberturas=[]
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
        if abertura_superior:
            cortes.append(abertura_superior)
        for x0,x1,y0,y1 in cortes:
            if x-ESPESOR<x1 and x+ESPESOR>x0:
                nuevos=[]
                for ya,yb in tramos:
                    if y0>ya:
                        nuevos.append((ya,min(y0,yb)))
                    if y1<yb:
                        nuevos.append((max(y1,ya),yb))
                tramos=[(a,b) for a,b in nuevos if b>a]
        for ya,yb in tramos:
            dibujar_refuerzo(ax,x,ya,ESPESOR,yb-ya,largo,h_izq,h_der,"pie_interior")
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
            if tipo in TIPOS_VENTANA and round(x1-x0)==1200 and abs(x-(x1-ESPESOR))<.001:
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
    largo_inclinado=(largo**2+dh**2)**.5
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

V1=(910,500,100,"V1")
V2=(910,500,-120,"V2")
V3=(1200,700,20,"V3")
P1=(762,2009,400,"P")
V4=(500,600,-320,"V4")
ventana_altillo=[910,583,515]

MUROS_LIB_02=[
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
        fig,ax=plt.subplots(figsize=(7,4))
        dibujar_muro_altillo(ax,largo,h_izq,h_der,viga,pies,aberturas,tiene_ventana_altillo,ventana_altillo[2])
        if tiene_ventana_altillo:
            dibujar_ventana_altillo(ax,largo,h_izq,h_der)
        dibujar_esquinas_L(ax,largo,h_izq,h_der,ESPESOR)
        ax.set_xlim(-150,largo+150)
        ax.set_ylim(-150,max(h_izq,h_der,viga)+300)
        ax.set_aspect("equal",adjustable="box")
        ax.grid(alpha=.3)
        ax.set_title(f"MURO {i}",fontsize=10)
        ax.tick_params(axis="both",labelsize=7)
        plt.tight_layout()
        figuras.append(fig)
    return figuras


# INTERFAZ STREAMLIT

st.set_page_config(page_title="Librerías Manulab",page_icon="🏗️",layout="wide")

st.markdown("""
<style>
.main-title{text-align:center;font-size:42px;font-weight:800;margin-bottom:4px}
.subtitle{text-align:center;color:#8a8a8a;font-size:16px;margin-bottom:28px}
div.stButton>button{width:100%;height:58px;font-size:18px;font-weight:700;border-radius:10px}
</style>
""",unsafe_allow_html=True)

st.markdown('<div class="main-title">LIBRERÍA MANULAB</div>',unsafe_allow_html=True)
st.markdown('<div class="subtitle">Biblioteca de componentes y estructuras de muros</div>',unsafe_allow_html=True)

if "libreria_seleccionada" not in st.session_state:
    st.session_state.libreria_seleccionada=None

col1,col2,col3=st.columns(3)

with col1:
    if st.button("LIB 00",key="lib00"):
        st.session_state.libreria_seleccionada="LIB 00"

with col2:
    if st.button("LIB 01",key="lib01"):
        st.session_state.libreria_seleccionada="LIB 01"

with col3:
    if st.button("LIB 02",key="lib02"):
        st.session_state.libreria_seleccionada="LIB 02"

st.divider()

def mostrar_figuras(figuras,columnas=2):
    for inicio in range(0,len(figuras),columnas):
        cols=st.columns(columnas)
        for j,figura in enumerate(figuras[inicio:inicio+columnas]):
            with cols[j]:
                st.pyplot(figura,use_container_width=True)
            plt.close(figura)

if st.session_state.libreria_seleccionada=="LIB 00":
    st.subheader("LIBRERÍA 00")
    st.info("Esta librería estará disponible próximamente.")

elif st.session_state.libreria_seleccionada=="LIB 01":
    st.subheader("LIBRERÍA 01")
    st.info("Esta librería estará disponible próximamente.")

elif st.session_state.libreria_seleccionada=="LIB 02":

    st.subheader("LIBRERÍA 02")
    st.caption("Componentes estructurales")

    st.markdown("### 1. Muros con ventanas y puertas")
    mostrar_figuras(generar_figuras_muros_aberturas())

    st.divider()
    st.markdown("### 2. Muros ciegos - Grupo 1")
    mostrar_figuras(generar_figuras_muros_ciegos(MUROS_CIEGOS,"Grupo 1"))

    st.divider()
    st.markdown("### 3. Muros ciegos - Grupo 2")
    mostrar_figuras(generar_figuras_muros_ciegos(MUROS_CIEGOS_2,"Grupo 2"))

    st.divider()
    st.markdown("### 4. Altillos")
    mostrar_figuras(generar_figuras_altillos_componentes())

    st.divider()
    st.markdown("### 5. Frontones triangulares")
    mostrar_figuras(generar_figuras_frontones())

    st.divider()
    st.markdown("### 6. Techumbres")
    mostrar_figuras(generar_figuras_techumbres())

    st.divider()
    st.markdown("### 7. Entrepisos")
    mostrar_figuras(generar_figuras_entrepisos())

    st.divider()
    st.markdown("### 8. Muros y altillos - LIB 02")
    mostrar_figuras(plot_muros_altillos(MUROS_LIB_02))

else:
    st.info("Selecciona una librería para visualizar su contenido.")


from typing import Optional
import geopandas as gpd
from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()
from math import *
import numpy as np

import matplotlib.pyplot as plt
import os
import time
import glob
from shapely.geometry import MultiPoint, Point
from shapely.geometry import mapping


#-----------------------------------------------------------------------------#
#Réchercjhes et affichage de parcelles grace aux infos telles que long et lat #
#-----------------------------------------------------------------------------#
class coordonnees(BaseModel):
    url:str 
    longitude:float
    latitude:float 
    
class coordinates(BaseModel):
    url:str
@app.post("/")
def recherche_parcelle(coords : coordonnees):
    df = gpd.read_file(coords.url, index = False)
    indice = df[df.LONGITUDE == coords.longitude].index[0] and df[df.LATITUDE == coords.latitude].index[0]
    return {str(indice), str(df.loc[indice])}


#------------------------------------------------------------------------#
#Obtention du dossier parent d'un fichier geojson oh sharp #
#------------------------------------------------------------------------#
@app.post("/url/")
def repertoire(coords : coordinates):
    url = str(coords.url)
    ab = url.split('/')
    del ab[-1]
    '/'.join(ab)
    ab.append('/')
    ab = '/'.join(ab)
    ab = ab[:-1]
  
    return {ab}


#------------------------------------------------------------------------#
#Création de code idufci technique avec des information suppléments      #
#------------------------------------------------------------------------#
class info_sup(BaseModel):
    domaine_foncier: int
    type_morcellement: str
    niveau_batiment: int
    nombre_appartement: int
@app.post("/_idufci_technique/")
def codification(coords : coordonnees, infos: info_sup):
    tab = []
    df = gpd.read_file(coords.url, index = False)
    indice = df[df.LONGITUDE == coords.longitude].index[0] and df[df.LATITUDE == coords.latitude].index[0]
    objectID = df.at[indice,'OBJECTID']
    #code longitude
    long = coords.longitude
    long = round(long, 4)
    q = str(long).split('.')

    signe = '0'
    if len(q[0]) < 2:
        codeL = signe + '0' + q[0] + q[1]
    elif len(q[0]) == 2:
        codeL = str(signe + q[0] + q[1])

    #code latitude
    lat = abs(coords.latitude)
    lat = round(lat, 4)
    q = str(lat).split('.')
    signe = '9'
    codelat = str(signe + q[0] + q[1])

    #code sommet
    sommet = df.at[indice, "NOMBRE_SOM"]
    aj = (4 - len(str(sommet)))
    if len(str(sommet)) < 3:
        codeSommet = aj * '0' + str(sommet)
    elif len(str(sommet)) == 3:
        codeSommet = str(sommet)
    
    #code perimètre
    perimetre = df.at[indice, "PERIMETRE"]
    aj = (4 - len(str(round(perimetre))))
    unites = ['0', '1', '2', '3']
    if 1 <= round(perimetre) <= 9999:
        codePerimetre = unites[0] + (aj * '0') + str(round(perimetre))
    if 10000 <= round(perimetre) <= 9999999:
        # if 5 <= len(str(p)) <= 7:
        coeff = int(str(1) + (len(str(round(perimetre))) - 4) * '0')
        codePerimetre = unites[1] + (aj * '0') + str(round(perimetre / coeff))
    if 10000000 <= round(perimetre) <= 999999999:
        # if 8 <= len(str(p)) <= 9:
        coeff = int(str(1) + (len(str(round(perimetre))) - 4) * '0')
        codePerimetre = unites[2] + (aj * '0') + str(round(perimetre / coeff))
    if round(perimetre) >= 1000000000:
        # if 10 <= len(str(p)):
        coeff = int(str(1) + (len(str(round(perimetre))) - 4) * '0')
        codePerimetre = unites[3] + (aj * '0') + str(round(perimetre / coeff))

    #code superficie
    superficie = df.at[indice, "SUPERFICIE"]
    aj = (5 - len(str(round(superficie))))
    unites = ['0', '1', '2', '3']
    if 1 <= round(superficie) <= 9999:
        codeSuperficie = unites[0] + (aj * '0') + str(round(superficie))
    if 10000 <= round(superficie) <= 9999999:
        # if 5 <= len(str(p)) <= 7:
        coeff = int(str(1) + (len(str(round(superficie))) - 4) * '0')
        codeSuperficie = unites[1] + (aj * '0') + str(round(superficie / coeff))
    if 10000000 <= round(superficie) <= 999999999:
        # if 8 <= len(str(p)) <= 9:
        coeff = int(str(1) + (len(str(round(superficie))) - 5) * '0')
        codeSuperficie = unites[2] + (aj * '0') + str(round(superficie / coeff))
    if round(superficie) >= 1000000000:
        # if 10 <= len(str(p)):
        coeff = int(str(1) + (len(str(round(codeSuperficie))) - 5) * '0')
        codeSuperficie = unites[3] + (aj * '0') + str(round(superficie / coeff))


#code domaine foncier

    n = infos.domaine_foncier
    aj = (3 - len(str(n)))
    if len(str(n)) != 3:
        codeDomaineFoncier = aj*'0' + str(n)
    elif len(str(n)) == 3:
        codeDomaineFoncier = str(n)

 
#code type morcellement
    choix = infos.type_morcellement
    choix = choix.upper()
    codeTypeMorcellement = choix

#code niveau batiment
    n = infos.niveau_batiment
    if len(str(n)) == 1:
        codeNiveauBatiment = '0' + str(n)
    elif len(str(n)) == 2:
        codeNiveauBatiment = n

#code nombre appartement
    n = infos.nombre_appartement
    aj = (3 - len(str(n)))
    if len(str(n)) != 3:
        codeNombreAppartement = aj*'0' + str(n)
    elif len(str(n)) == 3:
        codeNombreAppartement = str(n)

#génération du code
    for i in range(df.shape[0]):
        tab.append('0')
    df['IdufciTec'] = tab
    if df.at[indice,'IdufciTec'] == str(0):
        codeTech = codeL+codelat+codeSommet+codePerimetre+codeSuperficie+codeDomaineFoncier+codeTypeMorcellement+codeNiveauBatiment+codeNombreAppartement
        df['IdufciTec'] = np.where(df['OBJECTID']== objectID, codeTech, str(0))

    elif df.at[indice,'IdufciTec'] != str(0):
        print("Impossible d'ajouter, la parcelle a déjà un IDUFCI Technique")

#Création de dossier idufci technique
    url = str(coords.url)
    ab = url.split('/')
    del ab[-1]
    '/'.join(ab)
    ab.append('/')
    ab = '/'.join(ab)
    ab = ab[:-1]
    existence = ["CODE IDUFCI EXISTE", "VIDE"]
    tabex = []
    for i in range(df.shape[0]):
        tabex.append(existence[1])

    df['StatIdufci'] = tabex
    if df.at[indice, "StatIdufci"] == existence[0]:
        print(df.at[indice, "StatIdufci"])  
    elif df.at[indice, "StatIdufci"] == existence[1]:
        print("Statut idufci actuel :",df.at[indice, "StatIdufci"])
        print("Voulez-vous ajouter un code IDUFCI Technique à cette parcelle?")
        choix = input("O/n \n")
        if choix == 'O' and df.at[indice, "IdufciTec"] == '0':
            codeTech = codeL+codelat+codeSommet+codePerimetre+codeSuperficie+codeDomaineFoncier+codeTypeMorcellement+codeNiveauBatiment+codeNombreAppartement
            df['IdufciTec'] = np.where(df['OBJECTID']== objectID, codeTech, str(0))
            df['StatIdufci'] = np.where(df["OBJECTID"] == objectID, existence[0], existence[1]) 
            df.to_file(ab+'ITech_PARCELLE_'+df.at[indice,"PARCELLE"]+'.geojson')
        
    return {str(df.loc[indice])}


#------------------------------------------------------------------------#
#Vérification de la superposition d'une parcelle avec d'autres parcelles #
#------------------------------------------------------------------------#
@app.get("/_interceptes/")
def idufci(geojson_or_shap_url: str):
    return 0



#------------------------------------------------#
#Création du code idufci de manière automatique  #
#------------------------------------------------#

@app.get("/_tech/")
def idufci(geojson_or_shap_url: str):
    tab = []
    df = gpd.read_file(geojson_or_shap_url, index = False)
    index = df.index[0]

    #code longitude
    long = df.at[index,"LONGITUDE"]
    long = round(long, 4)
    q = str(long).split('.')

    signe = '0'
    if len(q[0]) < 2:
        codeL = signe + '0' + q[0] + q[1]
    elif len(q[0]) == 2:
        codeL = str(signe + q[0] + q[1])

    #code latitude
    lat = abs(df.at[index,"LATITUDE"])
    lat = round(lat, 4)
    q = str(lat).split('.')
    signe = '9'
    codelat = str(signe + q[0] + q[1])

    #code sommet
    sommet = df.at[index, "NOMBRE_SOM"]
    aj = (4 - len(str(sommet)))
    if len(str(sommet)) < 3:
        codeSommet = aj * '0' + str(sommet)
    elif len(str(sommet)) == 3:
        codeSommet = str(sommet)
    
    #code perimètre
    perimetre = df.at[index, "PERIMETRE"]
    aj = (4 - len(str(round(perimetre))))
    unites = ['0', '1', '2', '3']
    if 1 <= round(perimetre) <= 9999:
        codePerimetre = unites[0] + (aj * '0') + str(round(perimetre))
    if 10000 <= round(perimetre) <= 9999999:
        # if 5 <= len(str(p)) <= 7:
        coeff = int(str(1) + (len(str(round(perimetre))) - 4) * '0')
        codePerimetre = unites[1] + (aj * '0') + str(round(perimetre / coeff))
    if 10000000 <= round(perimetre) <= 999999999:
        # if 8 <= len(str(p)) <= 9:
        coeff = int(str(1) + (len(str(round(perimetre))) - 4) * '0')
        codePerimetre = unites[2] + (aj * '0') + str(round(perimetre / coeff))
    if round(perimetre) >= 1000000000:
        # if 10 <= len(str(p)):
        coeff = int(str(1) + (len(str(round(perimetre))) - 4) * '0')
        codePerimetre = unites[3] + (aj * '0') + str(round(perimetre / coeff))

    #code superficie
    superficie = df.at[index, "SUPERFICIE"]
    aj = (5 - len(str(round(superficie))))
    unites = ['0', '1', '2', '3']
    if 1 <= round(superficie) <= 9999:
        codeSuperficie = unites[0] + (aj * '0') + str(round(superficie))
    if 10000 <= round(superficie) <= 9999999:
        # if 5 <= len(str(p)) <= 7:
        coeff = int(str(1) + (len(str(round(superficie))) - 4) * '0')
        codeSuperficie = unites[1] + (aj * '0') + str(round(superficie / coeff))
    if 10000000 <= round(superficie) <= 999999999:
        # if 8 <= len(str(p)) <= 9:
        coeff = int(str(1) + (len(str(round(superficie))) - 5) * '0')
        codeSuperficie = unites[2] + (aj * '0') + str(round(superficie / coeff))
    if round(superficie) >= 1000000000:
        # if 10 <= len(str(p)):
        coeff = int(str(1) + (len(str(round(codeSuperficie))) - 5) * '0')
        codeSuperficie = unites[3] + (aj * '0') + str(round(superficie / coeff))


#génération du code
    tab = ['0']
    df['IdufciTec'] = tab
    objectID = df.at[index, "OBJECTID"]
    if df.at[index,'IdufciTec'] == str(0):
        codeTech = codeL+codelat+codeSommet+codePerimetre+codeSuperficie
        df['IdufciTec'] = np.where(df['OBJECTID']== objectID, codeTech, str(0))

    elif df.at[index,'IdufciTec'] != str(0):
        print("Impossible d'ajouter, la parcelle a déjà un IDUFCI Technique")

#Création de dossier idufci technique
    url = geojson_or_shap_url
    ab = url.split('/')
    del ab[-1]
    '/'.join(ab)
    ab.append('/')
    ab = '/'.join(ab)
    ab = ab[:-1]
    existence = ["CODE IDUFCI EXISTE", "VIDE"]
    tabex = [existence[-1]]
   
    df['StatIdufci'] = tabex
    if df.at[index, "StatIdufci"] == existence[0]:
        print(df.at[index, "StatIdufci"])  
    elif df.at[index, "StatIdufci"] == existence[1]:
        if df.at[index, "IdufciTec"] == '0':
            codeTech = codeL+codelat+codeSommet+codePerimetre+codeSuperficie
            df['IdufciTec'] = np.where(df['OBJECTID']== objectID, codeTech, str(0))
            df['StatIdufci'] = np.where(df["OBJECTID"] == objectID, existence[0], existence[1]) 
            df.to_file(str(ab)+'_PARCELLE_'+str(df.at[index,"PARCELLE"]))
    return {str(df.at[index, "IdufciTec"])}

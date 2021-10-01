import pandas as pd
import geopandas as gpd
import numpy as np
import sys 

#Recupération automatique
url = str(input("Entrez le chémin de votre fichier .geojson :"))
df = gpd.read_file(url, index = False)
index = df.index[0]

def repertoire(url):
    ab = url.split('/')
    del ab[-1]
    '/'.join(ab)
    ab.append('/')
    ab = '/'.join(ab)
    ab = ab[:-1]
    return ab




    


def codeLongitude():
    l = df.at[index,"LONGITUDE"] 
    l = round(l, 4)
    q = str(l).split('.')
    signe = '9'
    if len(q[0]) < 2:
        return signe + '0' + q[0] + q[1]
    elif len(q[0]) == 2:
        return str(signe + q[0] + q[1])


def codeLatitude():
    l = df.at[index,"LATITUDE"]
    l = -round(l, 4)
    q = str(l).split('.')
    signe = '0'
    return str(signe + q[0] + q[1])


def nbre_sommet():
    s = df.at[index,"NOMBRE_SOM"]
    aj = (4 - len(str(s)))
    if len(str(s)) < 3:
        code = aj * '0' + str(s)
    elif len(str(s)) == 3:
        code = str(s)
    return code


def codePerimetre():
    p = df.at[index,"PERIMETRE"]
    aj = (4 - len(str(round(p))))
    unites = ['0', '1', '2', '3']
    if 1 <= round(p) <= 9999:
        code = unites[0] + (aj * '0') + str(round(p))
    if 10000 <= round(p) <= 9999999:
        # if 5 <= len(str(p)) <= 7:
        coeff = int(str(1) + (len(str(round(p))) - 4) * '0')
        code = unites[1] + (aj * '0') + str(round(p / coeff))
    if 10000000 <= round(p) <= 999999999:
        # if 8 <= len(str(p)) <= 9:
        coeff = int(str(1) + (len(str(round(p))) - 4) * '0')
        code = unites[2] + (aj * '0') + str(round(p / coeff))
    if round(p) >= 1000000000:
        # if 10 <= len(str(p)):
        coeff = int(str(1) + (len(str(round(p))) - 4) * '0')
        code = unites[3] + (aj * '0') + str(round(p / coeff))
    return str(code)


def codeSuperficie():
    p = df.at[index,"SUPERFICIE"]
    aj = (5 - len(str(round(p))))
    unites = ['0', '1', '2', '3']
    if 1 <= round(p) <= 9999:
        code = unites[0] + (aj * '0') + str(round(p))
    if 10000 <= round(p) <= 9999999:
        # if 5 <= len(str(p)) <= 7:
        coeff = int(str(1) + (len(str(round(p))) - 4) * '0')
        code = unites[1] + (aj * '0') + str(round(p / coeff))
    if 10000000 <= round(p) <= 999999999:
        # if 8 <= len(str(p)) <= 9:
        coeff = int(str(1) + (len(str(round(p))) - 5) * '0')
        code = unites[2] + (aj * '0') + str(round(p / coeff))
    if round(p) >= 1000000000:
        # if 10 <= len(str(p)):
        coeff = int(str(1) + (len(str(round(p))) - 5) * '0')
        code = unites[3] + (aj * '0') + str(round(p / coeff))
    return str(code)





def _codeIDUFCITechnique():
    return ''.join([
    codeLongitude(),
    codeLatitude(),
    nbre_sommet(),
    codePerimetre(),
    codeSuperficie()])

#-------------------------------------Lecture fichier geojson et génération du code idufci technique 
#Une concaténation d tous ce qui precede sous certaines conditions
def genererIdufciTechnique(df):
    tab = []
    for i in range(df.shape[0]):
        tab.append('0')
    df['IdufciTechnique'] = tab

    objectID = df.at[index,'OBJECTID']
    if df.at[index,'IdufciTechnique'] == str(0):
        df['IdufciTechnique'] = np.where(df['OBJECTID']== objectID, _codeIDUFCITechnique(), str(0))
        return df.iloc[index-3:index+3]
    elif df.at[index,'IdufciTechnique'] != str(0):
        print("Impossible d'ajouter, la parcelle a déjà un IDUFCI Technique")
        return df.iloc[index:index+1]

#Vérification de l'existance de l'idufci sous certaine condition avec possibilité de créer un code udifci si la parcelle n'en n'a pas
def verificationCodeIDUFCITechnique():


    existence = ["CODE IDUFCI EXISTE", "VIDE"]
    index = df.index
    condition = df["OBJECTID"] == df.at[index,'OBJECTID']
    indice = index[condition]
    indice = indice.values[0]
    tab = []
    for i in range(df.shape[0]):
        tab.append(existence[1])

    df['StatutIDUFCITechnique'] = tab
    if df.at[indice, "StatutIDUFCITechnique"] == existence[0]:
        print(df.at[indice, "StatutIDUFCITechnique"])  
    elif df.at[indice, "StatutIDUFCITechnique"] == existence[1]:
        print(df.at[indice, "StatutIDUFCITechnique"])
        print("Voulez-vous ajouter un code IDUFCI Technique à cet identifiant?")
        choix = input("O/n \n")
        if choix == "O":
            genererIdufciTechnique(df)
            code = df.at[indice, "IdufciTechnique"]
            df['StatutIDUFCITechnique'] = np.where(df["OBJECTID"] == df.at[index,'OBJECTID'], existence[0], existence[1]) 
    df.to_file(''.join([repertoire(url),'IDUFCI_TECHNIQUE_PARCELLE_',str(df.at[indice,"PARCELLE"]),str('.geojson')]))
    return df[df["OBJECTID"] == df.at[index,'OBJECTID']]

print(verificationCodeIDUFCITechnique())
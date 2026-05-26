from flask import Flask, request, render_template
import joblib
import pandas as pd

app = Flask(__name__)

model = joblib.load('model.pkl')

def predict(input_features):
    input_df = pd.DataFrame([input_features], columns=['nbr_mot', 'longueur_moyenne_mot', 'nbr_0', 'nbr_1', 'longueur_max', 'longueur_min','apparition_0','apparition_1'])
    prediction = model.predict(input_df)
    return prediction[0]

def calcul_residuel(tab,mot):
    result=[]
    rep=0
    for i in range(0,len(tab)):
        if tab[i].startswith(mot):
            if tab[i]==mot:
                rep+=1
                if rep>1:
                    result.append('e')
                continue
            result.append(tab[i].removeprefix(mot))
    return result

def remplacerParEsp(tableau):
    for i in range(len(tableau)):
        for j in range(i+1, len(tableau)):
            if tableau[i] == tableau[j]:
                tableau[j] = "e"
    return tableau

def calcul_quotient(L,Ln):
    result=[]
    for ln in Ln:
        result.extend(calcul_residuel(L,ln))
    return remplacerParEsp(result)

def test_code(L):
    result=[]
    L0=L
    L1=calcul_quotient(L,L)
    result.append(L0)
    result.append(L1)
    Ln=L1
    index=2
    while "e" not in Ln:
        partieGauche=calcul_quotient(Ln,L)
        partieDroite=calcul_quotient(L,Ln)
        Ln=partieGauche+partieDroite
        if Ln in result:
            return 1
        result.append(Ln)
        index+=1
    return 0

def nombre_de_mot(tab):
    return len(tab)

def longueur_moyenne_mot(tab):
    total = sum(len(word) for word in tab)
    alavany = len(tab)
    if alavany == 0:
        return 0
    else:
        return total / alavany

def manisa_0(tab):
    return sum(word.count('0') for word in tab)

def manisa_1(tab):
    return sum(word.count('1') for word in tab)

def longueur_max(tab):
    if not tab:
        return 0
    return max(len(word) for word in tab)

def longueur_min(tab):
    if not tab:
        return 0
    return min(len(word) for word in tab)

def apparition_0(tab):
    total_caracteres = 0
    total_zero = 0
    for chaine in tab:
        total_caracteres += len(chaine)
        total_zero += chaine.count('0')
    if total_caracteres == 0:
        return 0
    taux = total_zero / total_caracteres
    return taux

def apparition_1(tab):
    total_caracteres = 0
    total_zero = 0
    for chaine in tab:
        total_caracteres += len(chaine)
        total_zero += chaine.count('1')
    if total_caracteres == 0:
        return 0
    taux = total_zero / total_caracteres
    return taux

@app.route('/', methods=['GET', 'POST'])
def input_langage():
    if request.method == 'POST':
        langage_input = request.form['langage']
        tab = eval(langage_input)

        row=[]
        row.append(nombre_de_mot(tab))
        row.append(longueur_moyenne_mot(tab))
        row.append(manisa_0(tab))
        row.append(manisa_1(tab))
        row.append(longueur_max(tab))
        row.append(longueur_min(tab))
        row.append(apparition_0(tab))
        row.append(apparition_1(tab))

        prediction = predict(row)
        sardinas_paterson_result = test_code(tab)
        return render_template('result.html', prediction=prediction, sardinas_paterson_result=sardinas_paterson_result)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

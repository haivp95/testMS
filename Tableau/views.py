from django.shortcuts import render
import json


def reportTableau (request, tableau):
    print(tableau)
    request.session['tableau'] = tableau
    return render(request, 'Tableau.html')

# def reportTableau (request, num=1):
#     print('1 nha')
#     return render(request, 'Tableau.html')
    

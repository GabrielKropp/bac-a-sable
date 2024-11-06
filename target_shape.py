import csv
import re
from prometheus_client import CollectorRegistry, Gauge, pushadd_to_gateway
import requests
from requests.auth import HTTPBasicAuth

# Chemin vers le fichier CSV
csv_file_path = 'votre_fichier.csv'
# Adresse du serveur VictoriaMetrics
victoria_url = 'http://votre_serveur_victoriametrics:9091'
# Informations d'authentification
username = 'votre_nom_utilisateur'
password = 'votre_mot_de_passe'

# Création d'un registre Prometheus
registry = CollectorRegistry()

# Initialisation d'une métrique de type Gauge
g = Gauge('debit_metric', 'Débit de la métrique', labelnames=['label1', 'label2', 'label3'], registry=registry)

# Fonction pour extraire et convertir le débit
def convertir_debit(valeur_debit):
    match = re.search(r'Débit\s*:\s*(\d+(\.\d+)?)\s*Mb/s', valeur_debit)
    if match:
        # Conversion en bits
        debit_mbps = float(match.group(1))
        debit_bits = int(debit_mbps * 1_000_000)
        return debit_bits
    else:
        print("Erreur : Débit introuvable dans", valeur_debit)
        return None

# Filtre de routeur
def filtre_routeur(nom_routeur):
    return re.search(r'c[0-2]$', nom_routeur) is not None

# Lecture du fichier CSV et ajout des valeurs à la métrique
with open(csv_file_path, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    for row in csv_reader:
        # Filtrer les lignes en fonction de nom_routeur
        if not filtre_routeur(row['nom_routeur']):
            continue  # Ignorer cette ligne si elle ne correspond pas au filtre
        
        # Récupérer et convertir le débit
        valeur_debit = row['debit']
        debit = convertir_debit(valeur_debit)
        if debit is None:
            continue  # Passer cette ligne si le débit n'est pas trouvé ou mal formaté
            
        label1 = row['label1']
        label2 = row['label2']
        label3 = row['label3']

        # Ajout de la métrique avec les labels et la valeur
        g.labels(label1=label1, label2=label2, label3=label3).set(debit)
        
        # Format de debug simulant le format pushadd_to_gateway
        print(f'debit_metric{{label1="{label1}", label2="{label2}", label3="{label3}"}} {debit}')

# Envoi de la métrique au serveur VictoriaMetrics avec authentification
pushadd_to_gateway(victoria_url, job='csv_to_prometheus', registry=registry, handler=lambda url, method, timeout, headers, data: requests.request(
    method, url, data=data, headers=headers, timeout=timeout, auth=HTTPBasicAuth(username, password)
))

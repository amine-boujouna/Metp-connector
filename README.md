# Metp-connector

🧠 Fonctionnement du script
🔎 Étapes :
Connexion à l’API Facebook via un token

Récupération des derniers posts d’une page (/posts)

Extraction :

Texte

Images (via attachments)

Commentaires (auteurs, textes, date)

Filtrage par mot-clé (ex: "Jacques Chirac")

Sauvegarde dans MongoDB (base : meta_data, collection : posts)

Chaque document sauvegardé ressemble à ceci :
{
  "post_id": "1234567890_0987654321",
  "text": "Le décès du président Jacques Chirac...",
  "images": ["https://..."],
  "comments": [
    {
      "author": "Jean Dupont",
      "text": "Un grand homme",
      "date": "2025-09-29T08:30:00Z"
    }
  ],
  "created_time": "2025-09-28T14:15:00Z",
  "date_collected": "2025-09-29T12:00:00Z"
}

python meta_connector.py

🛡️ Bonnes pratiques & recommandations
Limiter les appels API : ne pas dépasser les quotas imposés par Meta.

Ne jamais publier ton token en clair (utilise .env)

Respecter la RGPD : les données collectées doivent être utilisées de façon responsable.

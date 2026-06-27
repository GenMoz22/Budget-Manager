import os
from dotenv import load_dotenv

load_dotenv()

from src import create_app

app = create_app()

if __name__ == '__main__':
    # Rileva dinamicamente la porta dall'ambiente (ottimizzato per Koyeb, Render, Heroku)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1", host='0.0.0.0', port=port)
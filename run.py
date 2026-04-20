from dotenv import load_dotenv
load_dotenv()   # 👈 MUST BE FIRST

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

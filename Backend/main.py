from flask import Flask, jsonify, request
from flask_cors import CORS
import openai
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import time
import pyrebase
from firebase import firebase

config = {
    "apiKey": "AIzaSyD1dsZ590gGskokLvT40AlvpBfClaEAECk",
    "authDomain": "yemek-asistani.firebaseapp.com",
    "projectId": "yemek-asistani",
    "storageBucket": "yemek-asistani.appspot.com",
    "messagingSenderId": "335909231649",
    "appId": "1:335909231649:web:2da483d625eed3339bd760",
    "measurementId": "G-T86BVWV371",
    "databaseURL": ""
}

firebaseAuth = pyrebase.initialize_app(config)
auth = firebaseAuth.auth()
firebase = firebase.FirebaseApplication('https://yemek-asistani-default-rtdb.europe-west1.firebasedatabase.app/', None)


clientOpenAi = openai.OpenAI(api_key="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")
asisstantId = "asst_usWVBhJ0xAD3yDrQ2lKpmWZL"

qdrant_client = QdrantClient(
    "ead20606-651e-4ea2-a592-252e7ca6ed1e.europe-west3-0.gcp.cloud.qdrant.io",
    api_key="KDLJ23vjZkSUbyFXOXSytHH61po__Y61dNuI5p4OsfzGP_KD9SbF5Q",
)
encoder = SentenceTransformer("all-MiniLM-L6-v2")

app = Flask(__name__)
CORS(app)
logged_in = False
user = ""

@app.route("/")
def anasayfa():
    result = firebase.get('/diyetler', None)
    return str(result)

# Burada kullanıcı kayıt işlemleri gerçekleştirilecek.
# Her kullanıcı'ya bir thread oluşturulacak ve id'si database'e yazılacak.
@app.route('/signup', methods=["POST"])
def signup():
    data = request.json
    print(data)
    return jsonify({'success': True}), 200

# Kullanıcı login olabiliyor mu? Burada database'e sorgu atıp login işlemi gerçekleştirilecek.
# Eğer login olmuş ise "logged_in" global değişkenini true yapacak.
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    print(data)
    username = data.get('username')
    password = data.get('password')
    user = username
    # Kullanıcı adı ve şifrenin doğruluğunu kontrol etmek için gerekli işlemleri yapılacak
    # Örneğin, veritabanında kullanıcıyı arayın ve şifre kontrolü yapılacak
    return jsonify({'success': True}), 200


# Burada kullanıcının login olup olmadığını kontrol etmek için bir istek kullanıyoruz.
@app.route('/check_login')
def check_login():
    # Bu örnekte, her zaman oturum açmış kabul ediyoruz
    return jsonify({"logged_in": True})

# Burada qdrant'ta search işlemlerini yapacak. Eğer benzer bir veri görürse
# ve bu veri kullanıcının dataseti'nde yok ise ekleyecek var ise bir şey yapmayacak.
@app.route('/qdrantSearch', methods=['POST'])
def qdrantSearch():
    data =request.json
    if(check_login()== True):
        hits = qdrant_client.search(
            collection_name="my_books",
            query_vector=encoder.encode(data).tolist(),
            limit=1,
        )
        for hit in hits:
            print(hit.payload, "score:", hit.score)
    return jsonify({'success': True}), 200


# Burada kullanıcı login olmuş ise eğer onun database'inden alışkanlıklarını almak için kullanacağız.
@app.route('/qdrantGetHabits')
def qdrant():
    mesaj= "qdrant çalışıyor."
    return mesaj

# Burada openAi'a tarif için istek atılıyor. Tabiki kullanıcının alışkanlıkları veritabanından alınacak
# ve bu verilerde isteğe eklenecek ve istek atılacaktır. 


@app.route('/openAiReq')
def openAiRequest():
    thread = clientOpenAi.beta.threads.create(
        messages = [
        {
            "role": "user",
            "content": ""
        } 
        ]
    )
    # burada thread_id bilgisi database'den alınacak. Daha sonrasında aşağıdaki gibi o thread retrive edilecek.
    # thread = client.beta.threads.retrieve(thread_id)

    thread_id = thread.id
    message = "Keto Diet"
    message = clientOpenAi.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )
    run = clientOpenAi.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=asisstantId
    )
    while run.status != "completed":
        time.sleep(0.5)
        run = clientOpenAi.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
    
    messages= clientOpenAi.beta.threads.messages.list(thread_id=thread_id)
    new_message = messages.data[0].content[0].text.value
    return new_message

if __name__ == "__main__":
    app.run(debug=True)

import os
import re
import pickle
import pandas as pd
import torch
import torch.nn.functional as F
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# --- Perbaikan untuk Windows: Memaksa browser membaca file CSS dan JS dengan benar ---
import mimetypes
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')
# ----------------------------------------------------------------------------------

# Initialize Flask App
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Global Variables for Models and Data
MODELS = {
    'indobert': {
        'tokenizer': None,
        'model': None,
        'embeddings': None,
        'kb': None,
        'loaded': False,
        'error': None
    },
    'sbert': {
        'model': None,
        'embeddings': None,
        'kb': None,
        'loaded': False,
        'error': None
    }
}

# Preprocessing function from notebook
def preprocessing(text):
    if not isinstance(text, str):
        return ""
    # mengubah teks menjadi huruf kecil
    text = text.lower()
    # menghapus link url pada teks
    text = re.sub(r"http\S+", "", text)
    # menghapus teks selain huruf, angka, dan spasi
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    # menghapus spasi yang berlebih
    text = re.sub(r"\s+", " ", text).strip()
    return text

# IndoBERT Embedding Function (Mean Pooling)
def get_bert_embedding(texts, model, tokenizer):
    encoded = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors="pt"
    )
    with torch.no_grad():
        output = model(**encoded)
    
    token_embeddings = output.last_hidden_state
    attention_mask = encoded["attention_mask"]
    
    # Expand attention mask to match dimensions
    mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    summed = torch.sum(token_embeddings * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    sentence_embedding = summed / counts
    return sentence_embedding

# Load IndoBERT Model and Data
def load_indobert():
    print("=== Loading IndoBERT Model and Data ===")
    try:
        from transformers import AutoTokenizer, AutoModel
        
        # Get base directory of the script to resolve paths correctly
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load CSV
        csv_path = os.path.join(base_dir, 'knowledge_base_bert.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            # Ensure columns exist
            if 'pertanyaan' in df.columns and 'jawaban' in df.columns:
                MODELS['indobert']['kb'] = df
            else:
                raise ValueError("CSV columns mismatch in knowledge_base_bert.csv. Expected 'pertanyaan' and 'jawaban'.")
        else:
            raise FileNotFoundError(f"Knowledge base file {csv_path} not found.")

        # Load Pickle Embeddings
        pkl_path = os.path.join(base_dir, 'model_indobert.pkl')
        if os.path.exists(pkl_path):
            with open(pkl_path, 'rb') as f:
                embeddings = pickle.load(f)
            # Safe mapping to CPU if saved from GPU
            if isinstance(embeddings, torch.Tensor):
                embeddings = embeddings.to('cpu')
            MODELS['indobert']['embeddings'] = embeddings
        else:
            raise FileNotFoundError(f"Embeddings file {pkl_path} not found.")

        # Load HuggingFace Model & Tokenizer
        local_weights_path = os.path.join(base_dir, "pytorch_model.bin")
        model_name = "indobenchmark/indobert-base-p1"
        
        if os.path.exists(local_weights_path):
            print(f"Loading IndoBERT config & tokenizer from HuggingFace, and weights locally from {local_weights_path}...")
            from transformers import AutoConfig
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            config = AutoConfig.from_pretrained(model_name)
            model = AutoModel.from_config(config)
            
            # Load weights locally
            state_dict = torch.load(local_weights_path, map_location="cpu")
            model.load_state_dict(state_dict)
            print("IndoBERT loaded locally successfully!")
        else:
            print(f"Loading IndoBERT from HuggingFace Hub (fetching weights): {model_name}...")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            
        model.eval()
        
        MODELS['indobert']['tokenizer'] = tokenizer
        MODELS['indobert']['model'] = model
        MODELS['indobert']['loaded'] = True
        print("IndoBERT loaded successfully!")
    except Exception as e:
        MODELS['indobert']['error'] = str(e)
        print(f"Error loading IndoBERT: {e}")

# Load SBERT Model and Data
def load_sbert():
    print("=== Loading SBERT Model and Data ===")
    try:
        from sentence_transformers import SentenceTransformer, util
        
        # Get base directory of the script to resolve paths correctly
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load CSV
        csv_path = os.path.join(base_dir, 'knowledge_base.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if 'pertanyaan' in df.columns and 'jawaban' in df.columns:
                MODELS['sbert']['kb'] = df
            else:
                raise ValueError("CSV columns mismatch in knowledge_base.csv. Expected 'pertanyaan' and 'jawaban'.")
        else:
            raise FileNotFoundError(f"Knowledge base file {csv_path} not found.")

        # Load Pickle Embeddings
        pkl_path = os.path.join(base_dir, 'model_sbert.pkl')
        if os.path.exists(pkl_path):
            with open(pkl_path, 'rb') as f:
                embeddings = pickle.load(f)
            if isinstance(embeddings, torch.Tensor):
                embeddings = embeddings.to('cpu')
            MODELS['sbert']['embeddings'] = embeddings
        else:
            raise FileNotFoundError(f"Embeddings file {pkl_path} not found.")

        # Load SentenceTransformer Model
        local_path_sbert = os.path.join(base_dir, "local_sbert")
        # Check if local folder contains model configuration
        if os.path.exists(local_path_sbert) and os.path.exists(os.path.join(local_path_sbert, "config.json")):
            model_name = local_path_sbert
            print(f"Loading SBERT from local folder: {model_name}...")
        else:
            model_name = "paraphrase-multilingual-MiniLM-L12-v2"
            print(f"Loading SBERT from HuggingFace Hub: {model_name}...")
            
        model = SentenceTransformer(model_name)
        
        MODELS['sbert']['model'] = model
        MODELS['sbert']['loaded'] = True
        print("SBERT loaded successfully!")
    except Exception as e:
        MODELS['sbert']['error'] = str(e)
        print(f"Error loading SBERT: {e}")

# Load models at startup
load_indobert()

# Routes
@app.route('/')
def home():
    if os.path.exists(os.path.join('templates', 'index.html')):
        return render_template('index.html')
    elif os.path.exists(os.path.join('static', 'index.html')):
        return send_from_directory('static', 'index.html')
    else:
        return "Frontend files not found. Please create templates/index.html or static/index.html."

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    selected_model = data.get('model', 'indobert').lower()
    threshold = float(data.get('threshold', 0.70))
    
    if not user_message:
        return jsonify({
            'status': 'error',
            'message': 'Pesan tidak boleh kosong.'
        }), 400

    if selected_model != 'indobert':
        return jsonify({
            'status': 'error',
            'message': 'Hanya model IndoBERT yang aktif saat ini.'
        }), 400
        
    model_info = MODELS[selected_model]
    
    if not model_info['loaded']:
        if selected_model == 'indobert':
            load_indobert()
        elif selected_model == 'sbert':
            load_sbert()
        model_info = MODELS[selected_model]
        if not model_info['loaded']:
            return jsonify({
                'status': 'error',
                'message': f"Model {selected_model} gagal dimuat. Error: {model_info['error']}"
            }), 500

    try:
        clean_msg = preprocessing(user_message)
        
        if selected_model == 'indobert':
            tokenizer = model_info['tokenizer']
            model = model_info['model']
            kb = model_info['kb']
            embeddings = model_info['embeddings']
            
            query_embedding = get_bert_embedding([clean_msg], model, tokenizer)
            
            query_embedding = F.normalize(query_embedding, p=2, dim=1)
            normalized_kb_embeddings = F.normalize(embeddings, p=2, dim=1)
            
            scores = torch.matmul(query_embedding, normalized_kb_embeddings.T)[0]
            best_score = scores.max().item()
            best_index = scores.argmax().item()
            
        elif selected_model == 'sbert':
            model = model_info['model']
            kb = model_info['kb']
            embeddings = model_info['embeddings']
            from sentence_transformers import util
            
            query_embedding = model.encode(clean_msg, convert_to_tensor=True)
            
            scores = util.cos_sim(query_embedding, embeddings)[0]
            best_score = scores.max().item()
            best_index = scores.argmax().item()

        if best_score >= threshold:
            matched_question = kb.iloc[best_index]['pertanyaan']
            reply = kb.iloc[best_index]['jawaban']
            is_fallback = False
        else:
            matched_question = kb.iloc[best_index]['pertanyaan'] if len(kb) > 0 else "-"
            reply = "Maaf, saya belum menemukan jawaban yang sesuai dengan pertanyaan Anda. Silakan tanyakan hal lain seputar siklus menstruasi dan kesehatan reproduksi."
            is_fallback = True
            
        return jsonify({
            'status': 'success',
            'reply': reply,
            'similarity': round(best_score, 4),
            'matched_question': matched_question,
            'is_fallback': is_fallback,
            'model_used': selected_model
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"Terjadi kesalahan saat memproses chat: {str(e)}"
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = {}
    for name, info in MODELS.items():
        stats[name] = {
            'loaded': info['loaded'],
            'questions_count': len(info['kb']) if info['kb'] is not None else 0,
            'error': info['error'],
            'model_name': 'indobenchmark/indobert-base-p1' if name == 'indobert' else 'paraphrase-multilingual-MiniLM-L12-v2'
        }
    return jsonify(stats)

@app.route('/api/knowledge', methods=['GET'])
def get_knowledge():
    selected_model = request.args.get('model', 'indobert').lower()
    search_query = request.args.get('query', '').strip()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 12))
    
    if selected_model != 'indobert':
        return jsonify({'status': 'error', 'message': 'Hanya model IndoBERT yang aktif saat ini.'}), 400
        
    model_info = MODELS[selected_model]
    
    if not model_info['loaded']:
        if selected_model == 'indobert':
            load_indobert()
        elif selected_model == 'sbert':
            load_sbert()
        model_info = MODELS[selected_model]
        if not model_info['loaded'] or model_info['kb'] is None:
            return jsonify({'status': 'error', 'message': f'Database model {selected_model} belum berhasil dimuat.'}), 400
        
    kb = model_info['kb']
    
    if search_query:
        filtered_df = kb[
            kb['pertanyaan'].str.contains(search_query, case=False, na=False) |
            kb['jawaban'].str.contains(search_query, case=False, na=False)
        ]
    else:
        filtered_df = kb
        
    total_items = len(filtered_df)
    total_pages = max(1, (total_items + limit - 1) // limit)
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_df = filtered_df.iloc[start_idx:end_idx]
    
    items = []
    for _, row in paginated_df.iterrows():
        items.append({
            'pertanyaan': row['pertanyaan'],
            'jawaban': row['jawaban']
        })
        
    return jsonify({
        'status': 'success',
        'items': items,
        'page': page,
        'limit': limit,
        'total_items': total_items,
        'total_pages': total_pages
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
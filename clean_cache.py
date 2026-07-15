import os
import shutil
from huggingface_hub.constants import HF_HUB_CACHE

def clean_cache():
    print("=== Hugging Face Cache Cleaner ===")
    print(f"Direktori cache Hugging Face terdeteksi di: {HF_HUB_CACHE}")
    
    # Target folders to clean
    targets = [
        "models--indobenchmark--indobert-base-p1",
        "models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2"
    ]
    
    cleaned_any = False
    for target in targets:
        target_path = os.path.join(HF_HUB_CACHE, target)
        if os.path.exists(target_path):
            print(f"Menghapus cache korup: {target_path} ...")
            try:
                # Remove read-only files helper on Windows
                shutil.rmtree(target_path)
                print(f"Berhasil menghapus {target}!")
                cleaned_any = True
            except Exception as e:
                print(f"Gagal menghapus {target}: {e}")
                print("Silakan coba hapus folder tersebut secara manual.")
        else:
            print(f"Folder cache '{target}' tidak ditemukan (sudah bersih).")
            
    if cleaned_any:
        print("\nCache yang korup telah dibersihkan! Silakan jalankan kembali 'python app.py'.")
    else:
        print("\nTidak ada cache korup yang perlu dibersihkan.")

if __name__ == "__main__":
    clean_cache()

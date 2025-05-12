from sentence_transformers import SentenceTransformer
import os

# Create the models directory if it doesn't exist
models_dir = "models"
os.makedirs(models_dir, exist_ok=True)

print("Downloading the model. This may take a few minutes...")

# Download model
model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(model_name)

# Save it to the local path
model_path = os.path.join(models_dir, model_name)
model.save(model_path)

print(f"Model successfully downloaded and saved to: {os.path.abspath(model_path)}")
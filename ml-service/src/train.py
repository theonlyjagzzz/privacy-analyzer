import os
import torch
import pandas as pd
import numpy as np
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from tqdm import tqdm

# Optimize CPU thread allocation
torch.set_num_threads(os.cpu_count() or 4)

MODEL_NAME = "nlpaueb/legal-bert-base-uncased"
DATA_PATH = "data/processed/cleaned_opp115.csv"
SAVE_DIR = "models/legal_bert_opp115"

# Optimized for fast CPU training
BATCH_SIZE = 16
MAX_LEN = 64
EPOCHS = 1
LR = 3e-5

CATEGORIES = [
    "First Party Collection/Use",
    "Third Party Sharing/Change",
    "User Choice/Control",
    "User Access, Edit and Deletion",
    "Data Retention",
    "Data Security",
    "Policy Change",
    "International and Specific Audiences",
    "Do Not Track",
    "Other"
]

class PrivacyDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        labels = self.labels[idx]

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt"
        )

        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": torch.tensor(labels, dtype=torch.float)
        }

def train_epoch(model, loader, optimizer, scheduler, device, epoch):
    model.train()
    total_loss = 0
    loss_fn = torch.nn.BCEWithLogitsLoss()

    loop = tqdm(loader, desc=f"Epoch {epoch+1}/{EPOCHS}", leave=True)
    for batch in loop:
        optimizer.zero_grad()
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        outputs = model(input_ids, attention_mask=attention_mask)
        loss = loss_fn(outputs.logits, labels)
        loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()

        total_loss += loss.item()
        loop.set_postfix(loss=f"{loss.item():.4f}")

    return total_loss / len(loader)

def evaluate(model, loader, device):
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in tqdm(loader, desc="Evaluating", leave=False):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids, attention_mask=attention_mask)
            preds = torch.sigmoid(outputs.logits).cpu().numpy()
            
            all_preds.append(preds)
            all_labels.append(labels.cpu().numpy())

    all_preds = np.vstack(all_preds)
    all_labels = np.vstack(all_labels)

    binary_preds = (all_preds > 0.5).astype(int)
    micro_f1 = f1_score(all_labels, binary_preds, average="micro")
    macro_f1 = f1_score(all_labels, binary_preds, average="macro")

    return micro_f1, macro_f1

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Training on device: {device} using {torch.get_num_threads()} CPU threads")

    df = pd.read_csv(DATA_PATH)
    texts = df["text"].values
    labels = df[CATEGORIES].values

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.15, random_state=42
    )

    print(f"[*] Dataset split: {len(train_texts)} train | {len(val_texts)} validation")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, 
        num_labels=len(CATEGORIES),
        problem_type="multi_label_classification"
    ).to(device)

    train_dataset = PrivacyDataset(train_texts, train_labels, tokenizer, MAX_LEN)
    val_dataset = PrivacyDataset(val_texts, val_labels, tokenizer, MAX_LEN)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer, 
        num_warmup_steps=int(total_steps * 0.1), 
        num_training_steps=total_steps
    )

    print("[*] Beginning Legal-BERT Fine-Tuning...")
    for epoch in range(EPOCHS):
        loss = train_epoch(model, train_loader, optimizer, scheduler, device, epoch)
        micro_f1, macro_f1 = evaluate(model, val_loader, device)
        print(f"\nEpoch {epoch+1} Completed | Loss: {loss:.4f} | Val Micro-F1: {micro_f1:.4f} | Val Macro-F1: {macro_f1:.4f}\n")

    os.makedirs(SAVE_DIR, exist_ok=True)
    model.save_pretrained(SAVE_DIR)
    tokenizer.save_pretrained(SAVE_DIR)
    print("=" * 50)
    print(f"SUCCESS: Model saved to '{SAVE_DIR}'")
    print("=" * 50)

if __name__ == "__main__":
    main()
import torch
from transformers import BertTokenizer, BertForNextSentencePrediction, logging
import re

logging.set_verbosity_error()
device = torch.device("cpu") if torch.cuda.is_available() else torch.device("cpu")
model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
checkpoint = torch.load("model_epoch7.pth")
model.load_state_dict(checkpoint["model_state_dict"])
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

sent1 = "Ukraine invades Russia."
sent2 = "Ukraine wins the war against Russia"
inputs = tokenizer(sent1, sent2, return_tensors="pt", max_length=512, padding="max_length", truncation=True)
pred = model(**inputs.to(device))
print(torch.sigmoid(pred.logits))


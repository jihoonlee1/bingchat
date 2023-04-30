import torch
from transformers import BertTokenizer, BertForNextSentencePrediction

device = torch.device("cpu") if torch.cuda.is_available() else torch.device("cpu")
model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
checkpoint = torch.load("model_epoch5.pth")
model.load_state_dict(checkpoint["model_state_dict"])
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


sent1 = "Russia invades ukraine"
sent2 = "korea wins"
inputs = tokenizer(sent1, sent2, return_tensors="pt", max_length=512, padding="max_length", truncation=True)
pred = model(**inputs.to(device))
print(torch.sigmoid(pred.logits))


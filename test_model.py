import torch
from transformers import BertTokenizer, BertForNextSentencePrediction
import re

device = torch.device("cpu") if torch.cuda.is_available() else torch.device("cpu")
model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
checkpoint = torch.load("model_epoch11.pth")
model.load_state_dict(checkpoint["model_state_dict"])
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


sent1 = '''China Mobile to launch 5G services in 31 cities by end of 2023 China Mobile, the world's largest mobile operator by subscribers, announced that it will launch 5G services in 31 cities across China by the end of this year. The company said it has invested over 100 billion yuan ($15.4 billion) in 5G infrastructure and equipment, and plans to deploy more than 300,000 5G base stations by the end of 2023. China Mobile said it will offer 5G services in various sectors, such as smart city, industrial internet, healthcare, education and entertainment.'''
sent2 = '''China Mobile leads the world in 5G connections, surpassing 200 million subscribers China Mobile, the world's largest mobile operator by subscribers, announced that it has reached 200 million 5G subscribers, accounting for more than half of the global 5G market. The company said it has achieved a 21% penetration rate of 5G among its total user base, and plans to further expand its 5G network coverage and services. China Mobile said it will offer more than 400 5G applications in various sectors, such as smart city, industrial internet, healthcare, education and entertainment.'''
sent2 = sent2.replace("China Mobile", "Apple")
print(sent2)
inputs = tokenizer(sent1, sent2, return_tensors="pt", max_length=512, padding="max_length", truncation=True)
pred = model(**inputs.to(device))
print(torch.sigmoid(pred.logits))


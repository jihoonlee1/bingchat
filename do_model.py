import torch
import database
import random
import re
from transformers import BertTokenizer, BertForNextSentencePrediction, logging


logging.set_verbosity_error()
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
learning_rate = 0.0003
model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
optimizer = torch.optim.Adam(params=model.parameters(), lr=learning_rate)
batch_size = 16 
epochs = 4


def train_test_root_ids(cur):
	cur.execute("SELECT id FROM root_events")
	root_ids = cur.fetchall()
	num_roots = len(root_ids)
	train_idx = round(num_roots * 0.9)
	train_root_ids = root_ids[:train_idx]
	test_root_ids = root_ids[train_idx:]
	return train_root_ids, test_root_ids


def prepare_data(cur, root_ids):
	sent0 = []
	sent1 = []
	labels = []
	for root_id, in root_ids:
		cur.execute("SELECT content FROM events WHERE id = ?", (root_id, ))
		root_content, = cur.fetchone()
		cur.execute("SELECT child_event_id, is_follow_up FROM root_event_children WHERE root_event_id = ?", (root_id, ))
		for child_id, is_follow_up in cur.fetchall():
			cur.execute("SELECT content FROM events WHERE id = ?", (child_id, ))
			child_content, = cur.fetchone()
			sent0.append(root_content)
			sent1.append(child_content)
			if is_follow_up == 0:
				labels.append(1)
			elif is_follow_up == 1:
				labels.append(0)
	return sent0, sent1, labels


class EventDataset(torch.utils.data.Dataset):

	def __init__(self, encodings):
		self.input_ids = encodings["input_ids"]
		self.token_type_ids = encodings["token_type_ids"]
		self.attention_mask = encodings["attention_mask"]
		self.labels = encodings["labels"]

	def __len__(self):
		return len(self.input_ids)

	def __getitem__(self, idx):
		return {
			"input_ids": self.input_ids[idx],
			"token_type_ids": self.token_type_ids[idx],
			"attention_mask": self.attention_mask[idx],
			"labels": self.labels[idx]
		}


def train_loop(dataloader, epoch):
	num_dataloader = len(dataloader)
	total_loss = 0
	for batch in dataloader:
		input_ids = batch["input_ids"].to(device)
		token_type_ids = batch["token_type_ids"].to(device)
		attention_mask = batch["attention_mask"].to(device)
		labels = batch["labels"].to(device)
		output = model(input_ids=input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask, labels=labels)
		loss = output.loss
		optimizer.zero_grad()
		loss.backward()
		optimizer.step()
		loss_item = loss.item()
		total_loss += loss_item
		print(f"Loss: {loss_item}")
	avg_loss = total_loss / num_dataloader

	checkpoint = {
		"model_state_dict": model.state_dict(),
		"optimizer_state_dict": optimizer.state_dict(),
		"avg_loss": avg_loss,
		"epoch": epoch
	}
	torch.save(checkpoint, f"model_epoch{epoch}.pth")


def test_loop(dataloader, epoch):
	total_dataset = len(dataloader.dataset)
	num_dataloader = len(dataloader)
	total_loss = 0
	correct = 0
	with torch.no_grad():
		for batch in dataloader:
			input_ids = batch["input_ids"].to(device)
			token_type_ids = batch["token_type_ids"].to(device)
			attention_mask = batch["attention_mask"].to(device)
			labels = batch["labels"].to(device)
			output = model(input_ids=input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask, labels=labels)
			correct = correct + (output.logits.argmax(1) == labels.squeeze()).type(torch.float).sum().item()
			loss = output.loss
			loss_item = loss.item()
			print(f"Loss: {loss_item}")
			total_loss += loss_item
	avg_loss = total_loss / num_dataloader
	accuracy = correct / total_dataset

	with open("test.txt", "a") as f:
		f.write(f"model_epoch{epoch}.pth\taverage_loss: {avg_loss}\taccuracy: {accuracy}\n")


def main():
	with database.connect() as con:
		cur = con.cursor()
		train_ids, test_ids = train_test_root_ids(cur)
		sent0_train, sent1_train, labels_train = prepare_data(cur, train_ids)
		sent0_test, sent1_test, labels_test = prepare_data(cur, test_ids)

		encodings_train = tokenizer(sent0_train, sent1_train, return_tensors="pt", max_length=512, truncation=True, padding="max_length")
		encodings_train["labels"] = torch.LongTensor([labels_train]).T
		dataset_train = EventDataset(encodings_train)
		dataloader_train = torch.utils.data.DataLoader(dataset_train, batch_size=batch_size, shuffle=True)

		encodings_test = tokenizer(sent0_test, sent1_test, return_tensors="pt", max_length=512, truncation=True, padding="max_length")
		encodings_test["labels"] = torch.LongTensor([labels_test]).T
		dataset_test= EventDataset(encodings_test)
		dataloader_test = torch.utils.data.DataLoader(dataset_test, batch_size=batch_size, shuffle=True)

		for epoch in range(1, epochs+1):
			print(f"Epoch: {epoch}")
			train_loop(dataloader_train, epoch)
			test_loop(dataloader_test, epoch)


if __name__ == "__main__":
	main()

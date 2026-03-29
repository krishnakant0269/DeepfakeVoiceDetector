import torch
import torch.nn as nn
import torch.nn.functional as F
import librosa
import numpy as np


class AudioFeatureExtractor:
    def __init__(self, sample_rate=16000, n_mfcc=40, max_len=300):
        self.sample_rate = sample_rate
        self.n_mfcc = n_mfcc
        self.max_len = max_len

    def extract_features(self, audio_path):
        y, sr = librosa.load(audio_path, sr=self.sample_rate)

        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
        delta = librosa.feature.delta(mfcc)
        delta2 = librosa.feature.delta(mfcc, order=2)

        features = np.vstack([mfcc, delta, delta2])

        if features.shape[1] < self.max_len:
            pad_width = self.max_len - features.shape[1]
            features = np.pad(features, ((0, 0), (0, pad_width)), mode='constant')
        else:
            features = features[:, :self.max_len]

        return features.astype(np.float32)


class DeepfakeVoiceDetector(nn.Module):
    def __init__(self, input_channels=120, hidden_dim=128):
        super(DeepfakeVoiceDetector, self).__init__()

        self.conv1 = nn.Conv1d(input_channels, 128, kernel_size=5, padding=2)
        self.bn1 = nn.BatchNorm1d(128)

        self.conv2 = nn.Conv1d(128, 256, kernel_size=5, padding=2)
        self.bn2 = nn.BatchNorm1d(256)

        self.pool = nn.MaxPool1d(2)

        self.lstm = nn.LSTM(
            input_size=256,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            bidirectional=True
        )

        self.fc1 = nn.Linear(hidden_dim * 2, 64)
        self.fc2 = nn.Linear(64, 1)

        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))

        x = x.permute(0, 2, 1)

        lstm_out, _ = self.lstm(x)
        x = lstm_out[:, -1, :]

        x = self.dropout(F.relu(self.fc1(x)))
        x = torch.sigmoid(self.fc2(x))

        return x


class VoiceDeepfakeModel:
    def __init__(self, model_path=None, device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")

        self.feature_extractor = AudioFeatureExtractor()
        self.model = DeepfakeVoiceDetector().to(self.device)

        if model_path:
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))

        self.model.eval()

    def predict(self, audio_path):
        features = self.feature_extractor.extract_features(audio_path)
        features = torch.tensor(features).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(features)

        score = output.item()

        return {
            "score": score,
            "label": "AI Generated" if score > 0.5 else "Real Human Voice",
            "confidence": round(score * 100, 2)
        }


if __name__ == "__main__":
    model = VoiceDeepfakeModel()
    result = model.predict("sample.wav")
    print(result)

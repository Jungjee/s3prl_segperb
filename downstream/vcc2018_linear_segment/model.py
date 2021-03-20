import torch
import torch.nn as nn


class SelfAttentionPooling(nn.Module):
    """
    Implementation of SelfAttentionPooling
    Original Paper: Self-Attention Encoding and Pooling for Speaker Recognition
    https://arxiv.org/pdf/2008.01077v1.pdf
    """

    def __init__(self, input_dim):
        super(SelfAttentionPooling, self).__init__()
        self.W = nn.Linear(input_dim, 1)

    def forward(self, batch_rep):
        """
        input:
            batch_rep : size (N, T, H), N: batch size, T: sequence length, H: Hidden dimension

        attention_weight:
            att_w : size (N, T, 1)

        return:
            utter_rep: size (N, H)
        """
        softmax = nn.functional.softmax
        att_w = softmax(self.W(batch_rep).squeeze(-1)).unsqueeze(-1)
        utter_rep = torch.sum(batch_rep * att_w, dim=1)

        return utter_rep


class Model(nn.Module):
    def __init__(self, input_dim, clipping=False, attention_pooling=False, **kwargs):
        super(Model, self).__init__()
        self.linear = nn.Linear(input_dim, 1)
        self.clipping = clipping
        self.pooling = SelfAttentionPooling(input_dim) if attention_pooling else None

    def forward(self, features):
        if self.pooling is not None:
            x = self.pooling(features)
            segment_score = self.linear(x)
        else:
            x = self.linear(features)
            segment_score = x.squeeze(-1).mean(dim=-1)

        if self.clipping:
            segment_score = torch.tanh(segment_score) * 2 + 3

        return segment_score.squeeze(-1)

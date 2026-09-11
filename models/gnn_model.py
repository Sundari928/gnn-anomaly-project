"""
Lightweight Graph Neural Network for multivariate time-series anomaly detection.
Inspired by GDN (Deng & Hooi, AAAI 2021): learns a sensor-relationship graph via
node embeddings, then uses graph-attention based forecasting. Anomaly score =
deviation between predicted and actual sensor values at each timestep.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class GraphAttentionLayer(nn.Module):
    """Single-head graph attention over a fully-learnable sensor graph."""

    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.W = nn.Linear(in_dim, out_dim, bias=False)
        self.attn = nn.Linear(2 * out_dim, 1, bias=False)
        self.leaky_relu = nn.LeakyReLU(0.2)

    def forward(self, x, adj_logits):
        # x: (batch, num_nodes, in_dim); adj_logits: (num_nodes, num_nodes)
        h = self.W(x)  # (batch, N, out_dim)
        B, N, _ = h.shape
        h_i = h.unsqueeze(2).expand(B, N, N, -1)
        h_j = h.unsqueeze(1).expand(B, N, N, -1)
        e = self.leaky_relu(self.attn(torch.cat([h_i, h_j], dim=-1)).squeeze(-1))  # (B,N,N)
        e = e + adj_logits.unsqueeze(0)
        alpha = F.softmax(e, dim=2)
        out = torch.bmm(alpha, h)  # (B, N, out_dim)
        return out, alpha


class GDNLite(nn.Module):
    """
    Graph Deviation Network (lite).
    - Learns node (sensor) embeddings -> pairwise similarity -> soft adjacency.
    - Embeds a short window of history per sensor via GRU.
    - Graph-attention aggregates neighbor context to forecast next value.
    - Anomaly score = |predicted - actual|, normalized per-sensor.
    """

    def __init__(self, num_nodes, window_size, embed_dim=16, hidden_dim=32, topk=10):
        super().__init__()
        self.num_nodes = num_nodes
        self.window_size = window_size
        self.topk = min(topk, num_nodes - 1)

        self.node_embedding = nn.Embedding(num_nodes, embed_dim)
        self.gru = nn.GRU(input_size=1, hidden_size=hidden_dim, batch_first=True)
        self.gat = GraphAttentionLayer(hidden_dim, hidden_dim)
        self.predictor = nn.Sequential(
            nn.Linear(hidden_dim + embed_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )

    def build_graph(self):
        emb = self.node_embedding.weight  # (N, embed_dim)
        emb_n = F.normalize(emb, dim=1)
        sim = torch.matmul(emb_n, emb_n.t())  # cosine similarity (N, N)
        mask = torch.eye(self.num_nodes, device=emb.device).bool()
        sim = sim.masked_fill(mask, -1e9)
        # keep only top-k neighbors per node, rest -> -inf logit (no attention)
        topk_vals, topk_idx = torch.topk(sim, self.topk, dim=1)
        adj_logits = torch.full_like(sim, -1e9)
        adj_logits.scatter_(1, topk_idx, topk_vals)
        return adj_logits

    def forward(self, x):
        # x: (batch, window, num_nodes) -> per-node univariate window
        batch, window, N = x.shape
        x = x.permute(0, 2, 1).reshape(batch * N, window, 1)  # (batch*N, window, 1)
        _, h_n = self.gru(x)  # h_n: (1, batch*N, hidden_dim)
        h = h_n.squeeze(0).view(batch, N, -1)  # (batch, N, hidden_dim)

        adj_logits = self.build_graph()
        agg, _ = self.gat(h, adj_logits)  # (batch, N, hidden_dim)

        emb = self.node_embedding.weight.unsqueeze(0).expand(batch, -1, -1)
        combined = torch.cat([agg, emb], dim=-1)
        pred = self.predictor(combined).squeeze(-1)  # (batch, N)
        return pred

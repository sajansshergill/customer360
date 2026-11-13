from __future__ import annotations

import hashlib
from collections import defaultdict

from consumer360.utils.hashing import normalise_email, normalise_phone

MIN_FUZZY_CONFIDENCE = 0.70


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        if x not in self.parent:
            self.parent[x] = x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def _s(val) -> str:
    if val is None:
        return ""
    return str(val).strip()


def build_edges(profiles: list[dict]) -> list[dict]:
    """Return match edges with node_a, node_b, match_type, confidence."""
    edges: list[dict] = []
    by_node = {p["node_id"]: p for p in profiles}

    def add_edge(a: str, b: str, match_type: str, confidence: float) -> None:
        if a == b:
            return
        edges.append(
            {"node_a": a, "node_b": b, "match_type": match_type, "confidence": confidence}
        )

    by_cdc: dict[str, list[str]] = defaultdict(list)
    by_email: dict[str, list[str]] = defaultdict(list)
    by_phone: dict[str, list[str]] = defaultdict(list)
    by_device: dict[str, list[str]] = defaultdict(list)
    by_fuzzy: dict[tuple[str, str, str], list[str]] = defaultdict(list)

    for p in profiles:
        nid = p["node_id"]
        if p.get("cdc_id"):
            by_cdc[p["cdc_id"]].append(nid)
        email = normalise_email(p.get("email") or "")
        if email:
            by_email[email].append(nid)
        phone = normalise_phone(p.get("phone") or "")
        if phone:
            by_phone[phone].append(nid)
        device = (p.get("device_id") or "").strip()
        if device:
            by_device[device].append(nid)
        fuzzy_key = (
            _s(p.get("full_name")).lower(),
            _s(p.get("date_of_birth")),
            _s(p.get("zip_code")),
        )
        if all(fuzzy_key):
            by_fuzzy[fuzzy_key].append(nid)

    for group in by_cdc.values():
        for i in range(1, len(group)):
            add_edge(group[0], group[i], "cdc_id", 1.0)
    for group in by_email.values():
        for i in range(1, len(group)):
            add_edge(group[0], group[i], "verified_email", 1.0)
    for group in by_phone.values():
        for i in range(1, len(group)):
            add_edge(group[0], group[i], "phone", 0.98)

    for nodes in by_device.values():
        if len(nodes) < 2:
            continue
        emails = {normalise_email(by_node[n].get("email") or "") for n in nodes} - {""}
        if emails:
            for i in range(1, len(nodes)):
                add_edge(nodes[0], nodes[i], "device", 0.90)

    for nodes in by_fuzzy.values():
        if len(nodes) < 2:
            continue
        conf = 0.75
        if conf >= MIN_FUZZY_CONFIDENCE:
            for i in range(1, len(nodes)):
                add_edge(nodes[0], nodes[i], "fuzzy_name_dob", conf)

    return edges


def _golden_id_for_cluster(members: list[str], by_node: dict[str, dict]) -> str:
    cdc_ids = sorted({by_node[m]["cdc_id"] for m in members if by_node[m].get("cdc_id")})
    if cdc_ids:
        cdc = cdc_ids[0]
        if cdc.startswith("cdc_"):
            return "gold_" + cdc[4:]
        return f"gold_{cdc}"
    root = sorted(m for m in members if m) [0] if members else "unknown"
    h = hashlib.sha256(str(root).encode()).hexdigest()[:8]
    return f"gold_{h}"


def resolve_golden_ids(edges: list[dict], all_node_ids: list[str]) -> dict[str, str]:
    uf = UnionFind()
    for nid in all_node_ids:
        uf.find(nid)
    for e in edges:
        uf.union(e["node_a"], e["node_b"])

    clusters: dict[str, list[str]] = defaultdict(list)
    for nid in all_node_ids:
        clusters[uf.find(nid)].append(nid)

    by_node = {nid: {"cdc_id": None} for nid in all_node_ids}
    result: dict[str, str] = {}
    for members in clusters.values():
        gid = _golden_id_for_cluster(members, by_node)
        for m in members:
            result[m] = gid
    return result


def resolve_golden_ids_with_profiles(
    edges: list[dict], profiles: list[dict]
) -> dict[str, str]:
    uf = UnionFind()
    by_node = {p["node_id"]: p for p in profiles}
    all_node_ids = list(by_node.keys())
    for nid in all_node_ids:
        uf.find(nid)
    for e in edges:
        uf.union(e["node_a"], e["node_b"])

    clusters: dict[str, list[str]] = defaultdict(list)
    for nid in all_node_ids:
        clusters[uf.find(nid)].append(nid)

    result: dict[str, str] = {}
    for members in clusters.values():
        gid = _golden_id_for_cluster(members, by_node)
        for m in members:
            result[m] = gid
    return result

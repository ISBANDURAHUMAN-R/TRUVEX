from typing import List, Dict, Any

def generate_source_graph(
    url: str,
    platform: str,
    title: str,
    claims: List[Dict[str, Any]],
    overall_verdict: str,
    trust_score: int
) -> Dict[str, Any]:
    """
    Constructs node and edge structure representing the relationship:
    USER URL -> SOURCE PLATFORM -> ARTICLE/POST -> CLAIMS -> FACT-CHECK SOURCES -> EVIDENCE -> FINAL VERDICT
    """
    nodes = []
    edges = []

    # 1. User Input / URL Node
    user_node_id = "node_user_input"
    nodes.append({
        "id": user_node_id,
        "label": (url[:35] + "...") if url and len(url) > 35 else (url or "Direct Input"),
        "category": "url",
        "status": "neutral",
        "score": None
    })

    # 2. Platform Node
    platform_node_id = "node_platform"
    nodes.append({
        "id": platform_node_id,
        "label": platform,
        "category": "platform",
        "status": "neutral",
        "score": None
    })
    edges.append({
        "source": user_node_id,
        "target": platform_node_id,
        "label": "originated on",
        "relation": "origin"
    })

    # 3. Article / Post Node
    article_node_id = "node_article"
    nodes.append({
        "id": article_node_id,
        "label": (title[:40] + "...") if len(title) > 40 else title,
        "category": "content",
        "status": "neutral",
        "score": None
    })
    edges.append({
        "source": platform_node_id,
        "target": article_node_id,
        "label": "contains post",
        "relation": "contains"
    })

    # 4. Claims Nodes
    claim_node_ids = []
    for i, claim_item in enumerate(claims):
        cid = f"node_claim_{i+1}"
        claim_node_ids.append(cid)
        c_text = claim_item["claim"]
        c_verdict = claim_item["verdict"].lower()
        
        nodes.append({
            "id": cid,
            "label": f"Claim {i+1}: " + ((c_text[:35] + "...") if len(c_text) > 35 else c_text),
            "category": "claim",
            "status": c_verdict,
            "score": claim_item.get("confidence", 80)
        })
        edges.append({
            "source": article_node_id,
            "target": cid,
            "label": f"asserts",
            "relation": "extracts"
        })

        # Evidence / Source nodes for this claim
        supporting = claim_item.get("supporting_evidence", [])
        contradicting = claim_item.get("contradicting_evidence", [])

        # Add top supporting sources
        for s_idx, s in enumerate(supporting[:2]):
            s_id = f"node_src_supp_{i+1}_{s_idx+1}"
            nodes.append({
                "id": s_id,
                "label": s.get("source_name", "Fact Source"),
                "category": "source",
                "status": "true",
                "score": s.get("credibility_score", 85)
            })
            edges.append({
                "source": s_id,
                "target": cid,
                "label": "supports claim",
                "relation": "supports"
            })

        # Add top contradicting sources
        for c_idx, c in enumerate(contradicting[:2]):
            c_id = f"node_src_contra_{i+1}_{c_idx+1}"
            nodes.append({
                "id": c_id,
                "label": c.get("source_name", "Debunk Source"),
                "category": "source",
                "status": "false",
                "score": c.get("credibility_score", 85)
            })
            edges.append({
                "source": c_id,
                "target": cid,
                "label": "contradicts claim",
                "relation": "contradicts"
            })

    # 5. Final Verdict Node
    verdict_node_id = "node_verdict"
    v_status = "neutral"
    if "TRUE" in overall_verdict:
        v_status = "true"
    elif "FALSE" in overall_verdict:
        v_status = "false"
    elif "MISLEADING" in overall_verdict:
        v_status = "misleading"
    elif "UNVERIFIED" in overall_verdict:
        v_status = "unverified"

    nodes.append({
        "id": verdict_node_id,
        "label": f"Verdict: {overall_verdict}",
        "category": "verdict",
        "status": v_status,
        "score": trust_score
    })

    # Connect claims to final verdict
    for cid in claim_node_ids:
        edges.append({
            "source": cid,
            "target": verdict_node_id,
            "label": "informs verdict",
            "relation": "concludes"
        })

    return {
        "nodes": nodes,
        "edges": edges
    }

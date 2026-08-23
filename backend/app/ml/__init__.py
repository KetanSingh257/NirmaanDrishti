"""ML integration layer.

Cost and Time engines load artifacts from app/ml/{cost,time}/artifacts/
when present. Until then they fall back to deterministic mock predictors.
"""

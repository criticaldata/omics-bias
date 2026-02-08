from pathlib import Path

import plotly.graph_objects as go


def test_data_file_exists() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    data_path = repo_root / "data" / "bias.csv"
    assert data_path.exists(), "data/bias.csv is missing"


def test_kaleido_png_export() -> None:
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(label=["A", "B"]),
                link=dict(source=[0], target=[1], value=[1]),
            )
        ]
    )
    png_bytes = fig.to_image(format="png")
    assert isinstance(png_bytes, (bytes, bytearray))
    assert len(png_bytes) > 0

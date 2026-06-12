"""Build the Triton model repository the live-server CI job mounts.

One ONNX model, ``scorer``: sigmoid(W x + B) with the SAME fixed weights the frozen m26 live
test's descriptor declares — the descriptor is the served model's preserved identity, so the
two must agree by construction.

Usage: python scripts/make_triton_model_repo.py <repo-dir>
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper

SERVED_WEIGHT = 0.45
SERVED_BIAS = -0.1

CONFIG_PBTXT = """name: "scorer"
platform: "onnxruntime_onnx"
max_batch_size: 0
input [ { name: "x", data_type: TYPE_FP32, dims: [ -1, 1 ] } ]
output [ { name: "y", data_type: TYPE_FP32, dims: [ -1, 1 ] } ]
"""


def scorer_onnx() -> bytes:
    w = numpy_helper.from_array(np.array([[SERVED_WEIGHT]], dtype=np.float32), name="W")
    b = numpy_helper.from_array(np.array([SERVED_BIAS], dtype=np.float32), name="B")
    x = helper.make_tensor_value_info("x", TensorProto.FLOAT, [None, 1])
    y = helper.make_tensor_value_info("y", TensorProto.FLOAT, [None, 1])
    graph = helper.make_graph(
        [
            helper.make_node("Gemm", ["x", "W", "B"], ["z"]),
            helper.make_node("Sigmoid", ["z"], ["y"]),
        ],
        "scorer",
        [x],
        [y],
        initializer=[w, b],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)], ir_version=9)
    onnx.checker.check_model(model)
    return model.SerializeToString()  # type: ignore[no-any-return]


def main() -> None:
    repo = Path(sys.argv[1])
    model_dir = repo / "scorer" / "1"
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "model.onnx").write_bytes(scorer_onnx())
    (repo / "scorer" / "config.pbtxt").write_text(CONFIG_PBTXT)
    print(f"wrote Triton model repository: {repo}")


if __name__ == "__main__":
    main()

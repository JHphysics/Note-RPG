import { useEffect, useRef, useState } from "react";
import { generateItemFromSketch } from "../api";

const API_BASE = "http://localhost:8000";

export default function ItemSketchPad({ inventory, onItemImageUpdated }) {
  const canvasRef = useRef(null);

  const [drawing, setDrawing] = useState(false);
  const [selectedItemId, setSelectedItemId] = useState("");
  const [objectHint, setObjectHint] = useState("");
  const [detailHint, setDetailHint] = useState("");
  const [loading, setLoading] = useState(false);

  const [brushColor, setBrushColor] = useState("#000000");
  const [brushSize, setBrushSize] = useState(4);
  const [tool, setTool] = useState("brush"); // brush | eraser

  const [lastSketchUrl, setLastSketchUrl] = useState("");
  const [lastGeneratedUrl, setLastGeneratedUrl] = useState("");
  const [lastGeneratedItemName, setLastGeneratedItemName] = useState("");

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
  }, []);

  useEffect(() => {
    if (!selectedItemId) return;

    const selectedItem = inventory.find((item) => item.id === selectedItemId);
    if (selectedItem) {
      setObjectHint(selectedItem.name || "");
    }
  }, [selectedItemId, inventory]);

  const getContext = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    ctx.lineWidth = brushSize;
    ctx.strokeStyle = tool === "eraser" ? "#FFFFFF" : brushColor;
    ctx.globalCompositeOperation = "source-over";

    return ctx;
  };

  const getPos = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();

    if (e.touches && e.touches.length > 0) {
      return {
        x: e.touches[0].clientX - rect.left,
        y: e.touches[0].clientY - rect.top,
      };
    }

    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    };
  };

  const startDraw = (e) => {
    const ctx = getContext();
    const pos = getPos(e);

    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    setDrawing(true);
  };

  const draw = (e) => {
    if (!drawing) return;

    const ctx = getContext();
    const pos = getPos(e);

    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
  };

  const endDraw = () => {
    setDrawing(false);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  };

  const fillBackgroundWhite = (canvas) => {
    const tempCanvas = document.createElement("canvas");
    tempCanvas.width = canvas.width;
    tempCanvas.height = canvas.height;

    const tempCtx = tempCanvas.getContext("2d");
    tempCtx.fillStyle = "white";
    tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
    tempCtx.drawImage(canvas, 0, 0);

    return tempCanvas.toDataURL("image/png");
  };

  const handleGenerate = async () => {
    if (!selectedItemId) {
      alert("아이템을 선택해 주세요.");
      return;
    }

    const selectedItem = inventory.find((item) => item.id === selectedItemId);
    const canvas = canvasRef.current;
    const sketchDataUrl = fillBackgroundWhite(canvas);

    setLoading(true);
    try {
      const result = await generateItemFromSketch(
        selectedItemId,
        sketchDataUrl,
        objectHint,
        detailHint
      );

      setLastSketchUrl(`${API_BASE}${result.sketch_path}`);
      setLastGeneratedUrl(`${API_BASE}${result.image}`);
      setLastGeneratedItemName(result.name || selectedItem?.name || "");

      alert("스케치를 기반으로 아이템 이미지가 생성되었습니다.");
      onItemImageUpdated?.();
    } catch (err) {
      console.error(err);
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        marginTop: "24px",
        padding: "16px",
        border: "1px solid #ddd",
        borderRadius: "12px",
        background: "#fafafa",
      }}
    >
      <h3>아이템 스케치 → 이미지 생성</h3>

      <div style={{ marginBottom: "12px" }}>
        <label>아이템 선택</label>
        <br />
        <select
          value={selectedItemId}
          onChange={(e) => setSelectedItemId(e.target.value)}
          style={{ marginTop: "6px", padding: "8px", minWidth: "240px" }}
        >
          <option value="">선택하세요</option>
          {inventory.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name} ({item.id})
            </option>
          ))}
        </select>
      </div>

      <div style={{ marginBottom: "12px" }}>
        <label>이 그림이 무엇인지</label>
        <br />
        <input
          type="text"
          value={objectHint}
          onChange={(e) => setObjectHint(e.target.value)}
          placeholder="예: 낡은 편지"
          style={{
            marginTop: "6px",
            padding: "8px",
            width: "100%",
            boxSizing: "border-box",
          }}
        />
      </div>

      <div style={{ marginBottom: "12px" }}>
        <label>세부 설명</label>
        <br />
        <textarea
          value={detailHint}
          onChange={(e) => setDetailHint(e.target.value)}
          placeholder="예: 종이가 구겨져 있고 붉은 봉인 왁스가 붙어 있음"
          style={{
            marginTop: "6px",
            padding: "8px",
            width: "100%",
            minHeight: "80px",
            boxSizing: "border-box",
          }}
        />
      </div>

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "12px",
          alignItems: "center",
          marginBottom: "12px",
        }}
      >
        <div>
          <label>도구</label>
          <br />
          <button
            onClick={() => setTool("brush")}
            style={{
              marginTop: "6px",
              marginRight: "8px",
              background: tool === "brush" ? "#ddd" : "#fff",
            }}
          >
            브러시
          </button>
          <button
            onClick={() => setTool("eraser")}
            style={{
              marginTop: "6px",
              background: tool === "eraser" ? "#ddd" : "#fff",
            }}
          >
            지우개
          </button>
        </div>

        <div>
          <label>색상</label>
          <br />
          <input
            type="color"
            value={brushColor}
            disabled={tool === "eraser"}
            onChange={(e) => setBrushColor(e.target.value)}
            style={{ marginTop: "6px" }}
          />
        </div>

        <div>
          <label>굵기: {brushSize}</label>
          <br />
          <input
            type="range"
            min="1"
            max="24"
            value={brushSize}
            onChange={(e) => setBrushSize(Number(e.target.value))}
            style={{ marginTop: "6px" }}
          />
        </div>
      </div>

      {inventory.length === 0 && (
        <p style={{ color: "#999" }}>
          아이템을 먼저 획득하면 스케치를 사용할 수 있습니다.
        </p>
      )}

      <canvas
        ref={canvasRef}
        width={512}
        height={512}
        style={{
          border: "1px solid #ccc",
          borderRadius: "8px",
          background: "white",
          touchAction: "none",
          display: "block",
          marginBottom: "12px",
          maxWidth: "100%",
        }}
        onMouseDown={startDraw}
        onMouseMove={draw}
        onMouseUp={endDraw}
        onMouseLeave={endDraw}
        onTouchStart={startDraw}
        onTouchMove={draw}
        onTouchEnd={endDraw}
      />

      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <button onClick={clearCanvas}>지우기</button>
        <button onClick={handleGenerate} disabled={loading}>
          {loading ? "생성 중..." : "스케치로 생성"}
        </button>
      </div>

      {(lastSketchUrl || lastGeneratedUrl) && (
        <div style={{ marginTop: "20px" }}>
          <h4>스케치 / 생성 결과 비교</h4>
          {lastGeneratedItemName ? (
            <p style={{ color: "#666" }}>최근 생성 아이템: {lastGeneratedItemName}</p>
          ) : null}

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
              gap: "16px",
            }}
          >
            <div>
              <div style={{ fontWeight: "bold", marginBottom: "8px" }}>원본 스케치</div>
              {lastSketchUrl ? (
                <img
                  src={lastSketchUrl}
                  alt="원본 스케치"
                  style={{
                    width: "100%",
                    borderRadius: "10px",
                    border: "1px solid #ddd",
                    background: "white",
                  }}
                />
              ) : (
                <div>스케치 없음</div>
              )}
            </div>

            <div>
              <div style={{ fontWeight: "bold", marginBottom: "8px" }}>생성 결과</div>
              {lastGeneratedUrl ? (
                <img
                  src={lastGeneratedUrl}
                  alt="생성 결과"
                  style={{
                    width: "100%",
                    borderRadius: "10px",
                    border: "1px solid #ddd",
                    background: "white",
                  }}
                />
              ) : (
                <div>생성 결과 없음</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
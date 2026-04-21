import { useEffect, useRef, useState } from "react";
import { generateItemFromSketch } from "../api";

export default function ItemSketchPad({ inventory, onItemImageUpdated }) {
  const canvasRef = useRef(null);
  const [drawing, setDrawing] = useState(false);
  const [selectedItemId, setSelectedItemId] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.lineWidth = 4;
    ctx.lineCap = "round";
    ctx.strokeStyle = "black";
  }, []);

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
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const pos = getPos(e);

    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    setDrawing(true);
  };

  const draw = (e) => {
    if (!drawing) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
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

  const handleGenerate = async () => {
    if (!selectedItemId) {
      alert("아이템을 선택해 주세요.");
      return;
    }

    const canvas = canvasRef.current;
    const sketchDataUrl = canvas.toDataURL("image/png");

    setLoading(true);
    try {
      await generateItemFromSketch(selectedItemId, sketchDataUrl);
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
        background: "#fafafa"
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
          marginBottom: "12px"
        }}
        onMouseDown={startDraw}
        onMouseMove={draw}
        onMouseUp={endDraw}
        onMouseLeave={endDraw}
        onTouchStart={startDraw}
        onTouchMove={draw}
        onTouchEnd={endDraw}
      />

      <div style={{ display: "flex", gap: "10px" }}>
        <button onClick={clearCanvas}>지우기</button>
        <button onClick={handleGenerate} disabled={loading}>
          {loading ? "생성 중..." : "스케치로 생성"}
        </button>
      </div>
    </div>
  );
}
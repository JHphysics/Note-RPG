const API_BASE = "http://localhost:8000";

export default function SceneView({ scene, loading, onChoose }) {
  if (loading) {
    return <p>장면을 불러오는 중...</p>;
  }

  if (!scene) {
    return <p>장면 데이터가 없습니다.</p>;
  }

  return (
    <div style={{ maxWidth: "960px", margin: "0 auto" }}>
      <h1>{scene.title}</h1>

      {scene.image_url ? (
        <img
          src={scene.image_url}
          alt={scene.title}
          style={{
            width: "100%",
            maxWidth: "800px",
            borderRadius: "12px",
            display: "block",
            marginBottom: "16px"
          }}
        />
      ) : (
        <p>장면 이미지가 아직 없습니다.</p>
      )}

      <pre
        style={{
          whiteSpace: "pre-wrap",
          fontFamily: "inherit",
          lineHeight: 1.6,
          background: "#f5f5f5",
          padding: "16px",
          borderRadius: "12px"
        }}
      >
        {scene.description}
      </pre>

      <div style={{ marginTop: "20px" }}>
        <h3>선택지</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          {scene.choices.map((choice) => (
            <button
              key={choice.id}
              onClick={() => onChoose(choice.id)}
              style={{
                padding: "12px 16px",
                borderRadius: "10px",
                border: "1px solid #ccc",
                cursor: "pointer",
                textAlign: "left"
              }}
            >
              {choice.text}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginTop: "24px" }}>
        <h3>인벤토리</h3>

        {scene.inventory && scene.inventory.length > 0 ? (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "12px"
            }}
          >
            {scene.inventory.map((item) => (
              <div
                key={item.id}
                style={{
                  border: "1px solid #ddd",
                  borderRadius: "12px",
                  padding: "12px",
                  background: "#fff"
                }}
              >
                <div style={{ fontWeight: "bold", marginBottom: "8px" }}>
                  {item.name}
                </div>

                {item.image ? (
                  <img
                    src={`${API_BASE}${item.image}`}
                    alt={item.name}
                    style={{
                      width: "100%",
                      height: "160px",
                      objectFit: "cover",
                      borderRadius: "8px",
                      marginBottom: "8px",
                      border: "1px solid #eee"
                    }}
                  />
                ) : (
                  <div
                    style={{
                      width: "100%",
                      height: "160px",
                      borderRadius: "8px",
                      marginBottom: "8px",
                      border: "1px dashed #ccc",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "#999",
                      fontSize: "14px"
                    }}
                  >
                    이미지 없음
                  </div>
                )}

                <div style={{ fontSize: "14px", marginBottom: "8px" }}>
                  {item.description}
                </div>

                <div style={{ fontSize: "12px", color: "#666" }}>
                  태그: {item.tags?.join(", ") || "-"}
                </div>

                <div style={{ fontSize: "12px", color: "#666", marginTop: "6px" }}>
                  {item.quest_item ? "퀘스트 아이템" : "일반 아이템"}
                  {" / "}
                  {item.usable ? "사용 가능" : "사용 불가"}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>현재 보유한 아이템이 없습니다.</p>
        )}
      </div>

      <div style={{ marginTop: "20px" }}>
        <h3>현재 상태</h3>
        <pre
          style={{
            background: "#111",
            color: "#0f0",
            padding: "12px",
            borderRadius: "10px"
          }}
        >
          {JSON.stringify(scene.state, null, 2)}
        </pre>
      </div>
    </div>
  );
}
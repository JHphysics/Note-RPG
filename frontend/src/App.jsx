import { useEffect, useState } from "react";
import { fetchScene, chooseOption, setupGame } from "./api";
import SceneView from "./components/SceneView";
import ItemSketchPad from "./components/ItemSketchPad";
import GameSetupForm from "./components/GameSetupForm";

export default function App() {
  const [scene, setScene] = useState(null);
  const [loading, setLoading] = useState(false);
  const [gameReady, setGameReady] = useState(false);

  const startGame = async () => {
    setLoading(true);
    try {
      const data = await fetchScene("start", {
        inventory: []
      });
      setScene(data);
      setGameReady(true);
    } catch (err) {
      console.error(err);
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSetupGame = async (storyConfig) => {
    setLoading(true);
    try {
      await setupGame(storyConfig);
      const data = await fetchScene("start", {
        inventory: []
      });
      setScene(data);
      setGameReady(true);
    } catch (err) {
      console.error(err);
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const refreshScene = async () => {
    if (!scene) return;

    setLoading(true);
    try {
      const data = await fetchScene(scene.scene_id, scene.state);
      setScene(data);
    } catch (err) {
      console.error(err);
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChoose = async (choiceId) => {
    if (!scene) return;

    setLoading(true);
    try {
      const data = await chooseOption(scene.scene_id, choiceId, scene.state);
      setScene(data);
    } catch (err) {
      console.error(err);
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // 자동 시작 제거
  }, []);

  return (
    <div style={{ padding: "24px" }}>
      {!gameReady ? (
        <GameSetupForm onSubmit={handleSetupGame} loading={loading} />
      ) : (
        <>
          <button onClick={() => setGameReady(false)} style={{ marginBottom: "16px" }}>
            새 게임 설정
          </button>

          <SceneView scene={scene} loading={loading} onChoose={handleChoose} />

          {scene ? (
            <ItemSketchPad
              inventory={scene.inventory || []}
              onItemImageUpdated={refreshScene}
            />
          ) : null}
        </>
      )}
    </div>
  );
}
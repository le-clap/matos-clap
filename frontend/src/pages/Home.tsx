import ColorBends from "@/components/ui/ColorBends.tsx";

const Home = () => {
  return (
    <div className="relative w-full h-screen overflow-hidden">
      {/* Background Visuals */}
      <div className="absolute inset-0 z-0">
        <ColorBends
          speed={0.1}
          autoRotate={2}
          frequency={2.5}
          mouseInfluence={0}
          parallax={0.1}
          colors={["#e01b24", "#a51d2d", "#ffffff", "#3344aa"]}
        />
      </div>

      <div className="relative py-25 inset-0 z-0"></div>

    </div>
  );
};

export default Home;
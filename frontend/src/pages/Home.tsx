import ColorBends from "@/components/ColorBends";
// import CardNav from "@/components/CardNav";

const Home = () => {
  // Mapping the Architecture Doc to CardNav items

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

    </div>
  );
};

export default Home;
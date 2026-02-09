import FuzzyText from "@/components/ui/FuzzyText.tsx";

const Error = () => {
  return (
    <div className="min-h-auto flex flex-col items-center justify-center bg-[#1a1a1a] pt-40 pb-20 pr-9 gap-5">

      <FuzzyText
        baseIntensity={0.2}
        hoverIntensity={0.5}
        enableHover
        letterSpacing={2}
        clickEffect
      >
        404
      </FuzzyText>

      <FuzzyText
        baseIntensity={0.2}
        hoverIntensity={0.5}
        enableHover
        letterSpacing={2}
        clickEffect
      >
        not found
      </FuzzyText>

    </div>
  );
};

export default Error;
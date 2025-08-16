// Shamefully stolen from https://dev.to/jackherizsmith/making-a-progress-circle-in-react-3o65

const cleanPercentage = (percentage: number) => {
  const isNegativeOrNaN = !Number.isFinite(+percentage) || percentage < 0; // we can set non-numbers to 0 here
  const isTooHigh = percentage > 100;
  return isNegativeOrNaN ? 0 : isTooHigh ? 100 : +percentage;
};

const Circle = ({ colour, percentage } : {percentage: number, colour: string}) => {
  const r = 70;
  const circ = 2 * Math.PI * r;
  const strokePct = ((100 - percentage) * circ) / 100; // where stroke will start, e.g. from 15% to 100%.
  return (
    <circle
      r={r}
      cx={100}
      cy={100}
      fill="transparent"
      stroke={strokePct !== circ ? colour : ""} // remove colour as 0% sets full circumference
      strokeWidth={"2rem"}
      strokeDasharray={circ}
      strokeDashoffset={percentage ? strokePct : 0}
    ></circle>
  );
};

const Text = ({ percentage }: {percentage: number}) => {
  return (
    <text
      x="50%"
      y="50%"
      dominantBaseline="central"
      textAnchor="middle"
      fontSize={"1.5em"}
    >
      {percentage.toFixed(0)}%
    </text>
  );
};

export default function ProgressCircle({
  percentage,
}: {
  percentage: number
}) {
  const pct = cleanPercentage(percentage)
  return (
    <svg
      viewBox="0 0 200 200"
      width={100}
      height={100}
    >
     {/* white fill behind the circles */}
     <circle cx="100" cy="100" r={70} fill="white" />
      <g transform="rotate(-90 100 100)">
        <Circle colour="var(--incomplete)" percentage={100} />
        <Circle colour="var(--complete)" percentage={pct} />
      </g>
      <Text percentage={pct} />
    </svg>
  )
}
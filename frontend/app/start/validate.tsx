import { CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon } from "@heroicons/react/24/solid";
import { DescriptionDetails, DescriptionList, DescriptionTerm } from '@/components/description-list'

type ValidationCheck = {
  status: number;
  percentage: number | null;
  message: string;
  relevant: string[];
};

export default function ValidateSection({ checks }: { checks: ValidationCheck[] }) {
  const getStatusIcon = (status: number) => {
    switch (status) {
      case 0: return <CheckCircleIcon className="h-6 w-6 text-green-500" />;
      case 1: return <ExclamationTriangleIcon className="h-6 w-6 text-yellow-500" />;
      case 2: return <XCircleIcon className="h-6 w-6 text-red-500" />;
      default: return null;
    }
  };

  return (
<div className="space-y-4">
  {checks.map((check, i) => {
    const pct = check.percentage !== null ? Math.abs(check.percentage) : 0;
    const message =
      check.status === 0 && (!check.message || check.message.trim() === "")
        ? "✅ Meets requirement"
        : check.message;

    return (
      <div
        key={i}
        className="flex flex-col gap-2 rounded-xl border p-2 pb-4 shadow-sm bg-white"
      >
      <DescriptionList>
        <DescriptionTerm className="flex items-center gap-2">
          <div className="shrink-0">{getStatusIcon(check.status)}</div>
          {pct !== null && (
            <p className="text-sm text-gray-500">Progress: {pct}%</p>
          )}
        </DescriptionTerm>

        <DescriptionDetails className="font-medium flex text-gray-900">
          {message}
        </DescriptionDetails>

      </DescriptionList>
        {/* Relevant Courses (bottom row) */}
        {check.relevant.length > 0 && (
          <div className="mt-auto text-sm text-gray-600">
            Relevant Courses:{" "}
            {check.relevant.map((c, idx) => (
              <span
                key={idx}
                className="inline-block rounded bg-gray-100 px-2 py-0.5 mr-1 text-xs font-medium text-gray-700"
              >
                {c}
              </span>
            ))}
          </div>
        )}
      </div>
    );
  })}
</div>

  );
}

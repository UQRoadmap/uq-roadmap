"use client"

import { CheckCircleIcon } from "@heroicons/react/16/solid";
import { useEffect, useState } from "react";
import ValidateSection from "./validate";
import { XCircleIcon } from "@heroicons/react/16/solid";
import { XMarkIcon } from "@heroicons/react/16/solid";
import { ExclamationTriangleIcon } from "@heroicons/react/16/solid";

type ValidationCheck = {
  status: number;
  percentage: number | null;
  message: string;
  relevant: string[];
};

export default function PlanValidation({plan}: { plan: { id: string } }) {
    const [validate, setValidate] = useState<ValidationCheck[] | null>(null);
    const [isPlanDialogOpen, setIsPlanDialogOpen] = useState(false);

    useEffect(() => {
        async function fetchValidate() {
            try {
                // Add leading slash to the URL
                const res = await fetch(`/api/plan/${plan.id}/validate`);
                const data = await res.json();
                setValidate(data);
                console.log(data)
            } catch (err) {
                console.error("Error fetching validation data:", err);
            }
        }

        fetchValidate();
    }, [plan.id]);


    return (
        <div>
            {
                Array.isArray(validate) ? (
                    validate.length > 0 && validate.every((item: ValidationCheck) => item?.percentage === 100) ? (
                        <div className="relative inline-block">
                            <button
                                className="rounded-full p-0 shadow-none hover:shadow-md hover:cursor-pointer"
                                aria-label="all-fulfilled"
                                onClick={() => {
                                    setIsPlanDialogOpen(true);
                                    document.body.style.overflow = "hidden";
                                }}
                            >
                                <CheckCircleIcon className="h-10 w-10 bg-white rounded-full p-1 text-green-500 shadow" />
                            </button>

                            {isPlanDialogOpen && (
                                <div
                                    role="dialog"
                                    aria-modal="true"
                                    className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 p-4"
                                    onClick={() => {
                                        setIsPlanDialogOpen(false);
                                        document.body.style.overflow = "";
                                    }}
                                >
                                    <div
                                        className="bg-white text-black rounded shadow-lg w-full max-w-3xl max-h-[90vh] overflow-auto"
                                        onClick={(e) => e.stopPropagation()}
                                    >
                                        <div className="flex items-center justify-between p-4 border-b">
                                            <div className="font-semibold">Validation</div>
                                            <button
                                                aria-label="Close validation modal"
                                                className="text-gray-600 hover:text-red-500 hover:cursor-pointer"
                                                onClick={() => {
                                                    setIsPlanDialogOpen(false);
                                                    document.body.style.overflow = "";
                                                }}
                                            >
                                                <XMarkIcon className="h-5 bg-white" />
                                            </button>
                                        </div>
                                        <div className="p-4">
                                            <ValidateSection checks={validate} />
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="relative inline-block">
                            <button
                                className="bg-white rounded-full p-1 shadow hover:shadow-md text-red-500 hover:cursor-pointer"
                                aria-label="not-all-fulfilled"
                                onClick={() => {
                                    setIsPlanDialogOpen(true);
                                    document.body.style.overflow = "hidden";
                                }}
                            >
                                <XCircleIcon className="h-10 w-10 text-red-500" />
                            </button>

                            {isPlanDialogOpen && (
                                <div
                                    role="dialog"
                                    aria-modal="true"
                                    className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 p-4"
                                    onClick={() => {
                                        setIsPlanDialogOpen(false);
                                        document.body.style.overflow = "";
                                    }}
                                >
                                    <div
                                        className="bg-white text-black rounded shadow-lg w-full max-w-3xl max-h-[90vh] overflow-auto"
                                        onClick={(e) => e.stopPropagation()}
                                    >
                                        <div className="flex items-center justify-between p-4 border-b">
                                            <div className="font-semibold">Validation</div>
                                            <button
                                                aria-label="Close validation modal"
                                                className="text-gray-600 hover:text-red-500 hover:cursor-pointer"
                                                onClick={() => {
                                                    setIsPlanDialogOpen(false);
                                                    document.body.style.overflow = "";
                                                }}
                                            >
                                                <XMarkIcon className="h-5" />
                                            </button>
                                        </div>
                                        <div className="p-4">
                                            <ValidateSection checks={validate} />
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )
                ) : (
                    <div className="relative inline-block group">
                        <button
                            className="bg-white rounded-full p-1 shadow hover:shadow-md text-gray-400 hover:cursor-pointer"
                            aria-label="unknown"
                            onClick={() => {
                                setIsPlanDialogOpen(true);
                                document.body.style.overflow = "hidden";
                            }}
                        >
                            <ExclamationTriangleIcon className="h-10 w-10 text-yellow-500" />
                        </button>

                        <div className="pointer-events-none group-hover:pointer-events-auto opacity-0 group-hover:opacity-100 transition-opacity absolute right-0 mt-2 w-48 p-2 bg-white text-black rounded shadow-lg z-50">
                            <div className="text-sm">Validation unavailable</div>
                        </div>

                        {isPlanDialogOpen && (
                            <div
                                role="dialog"
                                aria-modal="true"
                                className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 p-4"
                                onClick={() => {
                                    setIsPlanDialogOpen(false);
                                    document.body.style.overflow = "";
                                }}
                            >
                                <div
                                    className="bg-white text-black rounded shadow-lg w-full max-w-3xl max-h-[90vh] overflow-auto"
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    <div className="flex items-center justify-between p-4 border-b">
                                        <div className="font-semibold">Validation</div>
                                        <button
                                            aria-label="Close validation modal"
                                            className="text-gray-600 hover:text-red-500 hover:cursor-pointer"
                                            onClick={() => {
                                                setIsPlanDialogOpen(false);
                                                document.body.style.overflow = "";
                                            }}
                                        >
                                            <XMarkIcon className="h-5" />
                                        </button>
                                    </div>
                                    <div className="p-4">
                                        <ValidateSection checks={validate ?? []} />
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )
            }
        </div>
    )
}
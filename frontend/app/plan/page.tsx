"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/button";
import { Dropdown, DropdownButton, DropdownItem, DropdownMenu } from "@/components/dropdown";
import { EllipsisVerticalIcon } from "@heroicons/react/16/solid";
import { Dialog, DialogActions, DialogBody, DialogDescription, DialogTitle } from "@/components/dialog";

type PlanData = {
    id: string;
    degree: string;
    startYear: string;
    endYear: string;
    unitsRemaining: number;
    major?: string;
    minor?: string;
    plannedCompleteSem: string;
    title?: string;
};

export default function PlanPage() {
    const router = useRouter();
    const [plans, setPlans] = useState<Array<{ key: string; id: string; data: PlanData | null }>>([]);
    const [isDeleteOpen, setIsDeleteOpen] = useState(false);
    const [deleteKey, setDeleteKey] = useState<string | null>(null);

    const handleDelete = (key: string | null) => {
        if (!key) return;
        if (typeof window === "undefined") return;
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error("Failed to remove plan", key, e);
        }
        setPlans(prev => prev.filter(p => p.key !== key));
        setIsDeleteOpen(false);
        setDeleteKey(null);
    };

    return (
        <>
        <main className="max-w-7xl mx-auto px-8 mt-4">
            <h1 className="text-2xl font-bold mb-6">Your Plans</h1>

            {plans.length === 0 && (
                <div className="text-center p-8 bg-gray-50 rounded-lg">
                    <p>You haven&apos;t created any plans yet.</p>
                    <Button
                        onClick={() => router.push('/start')}
                        accent
                        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        Create Your First Plan
                    </Button>
                </div>
            )}

            <ul className="space-y-4">
                {plans.map(({ key, id, data }) => (
                    <li key={key} className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                        <div className="p-4 bg-white">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h2 className="text-xl font-semibold">{data?.title || "Unknown Degree"}</h2>
                                    <div className="text-sm text-gray-500 mt-1">
                                        {data?.major && <span className="">Major: {data.major}</span>}
                                        {data?.minor && <span className="ml-2">• Minor: {data.minor}</span>}
                                    </div>
                                    <div className="text-sm mt-2">
                                        <span>{data?.startYear || "?"} to {data?.endYear || "?"}</span>
                                    </div>
                                </div>
                                <div className="flex space-x-2">
                                    <Button
                                        onClick={() => {
                                            console.log("")
                                        }}
                                        accent
                                        className="px-3 py-1"
                                    >
                                        Open Plan
                                    </Button>
                                    <Button
                                        onClick={() => {
                                            console.info("WHY")
                                        }}
                                        className="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300"
                                    >
                                        Refresh
                                    </Button>
                                    <Dropdown>
                                        <DropdownButton icon>
                                            <EllipsisVerticalIcon />
                                        </DropdownButton>
                                        <DropdownMenu>
                                            <DropdownItem
                                                onClick={() => {
                                                    setDeleteKey(key);
                                                    setIsDeleteOpen(true);
                                                }}
                                                className="hover:cursor-pointer"
                                            >
                                                Delete
                                            </DropdownItem>
                                        </DropdownMenu>
                                    </Dropdown>
                                </div>
                            </div>

                            {data?.unitsRemaining && (
                                <div className="mt-4">
                                    <div className="flex justify-between text-sm mb-1">
                                        <span>Units Remaining: {data.unitsRemaining}</span>
                                        <span>{Math.round((data.unitsRemaining / (data?.unitsRemaining || 1)) * 100)}% Remaining</span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                                        <div
                                            className="bg-blue-600 h-2.5 rounded-full"
                                            style={{ width: `${100 - Math.round((data.unitsRemaining / (data?.unitsRemaining || 1)) * 100)}%` }}
                                        ></div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </li>
                ))}
            </ul>
        </main>

        <Dialog
            open={isDeleteOpen}
            onClose={(open: boolean) => {
                setIsDeleteOpen(open);
                if (!open) setDeleteKey(null);
            }}
        >
            <DialogTitle>Delete plan</DialogTitle>
            <DialogDescription>Are you sure you want to delete this plan? This action cannot be undone.</DialogDescription>
            <DialogBody>
                <p className="text-sm text-gray-600">This will permanently remove the selected plan.</p>
            </DialogBody>
            <DialogActions>
                <Button onClick={() => { setIsDeleteOpen(false); setDeleteKey(null); }} outline>
                    Cancel
                </Button>
                <Button onClick={() => handleDelete(deleteKey)} accent>
                    Delete
                </Button>
            </DialogActions>
        </Dialog>
        </>
    );
}
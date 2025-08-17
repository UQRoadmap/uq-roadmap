"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/button";
import { Dropdown, DropdownButton, DropdownItem, DropdownMenu } from "@/components/dropdown";
import { EllipsisVerticalIcon } from "@heroicons/react/16/solid";
import { Dialog, DialogActions, DialogBody, DialogDescription, DialogTitle } from "@/components/dialog";
import { APIPlanRead } from "@/app/api/plan/types";

export default function PlanPage() {
    const router = useRouter();
    const [plans, setPlans] = useState<APIPlanRead[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isDeleteOpen, setIsDeleteOpen] = useState(false);
    const [deletePlanId, setDeletePlanId] = useState<string | null>(null);
    const [deleting, setDeleting] = useState(false);

    // Fetch plans on component mount
    useEffect(() => {
        fetchPlans();
    }, []);

    const fetchPlans = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await fetch('/api/plan');

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to fetch plans');
            }

            const plansData: APIPlanRead[] = await response.json();
            setPlans(plansData);
        } catch (err) {
            console.error('Error fetching plans:', err);
            setError(err instanceof Error ? err.message : 'Failed to load plans');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (planId: string | null) => {
        if (!planId) return;

        try {
            setDeleting(true);
            const response = await fetch(`/api/plan/${planId}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to delete plan');
            }

            // Remove from local state
            setPlans(prev => prev.filter(p => p.plan_id !== planId));
            setIsDeleteOpen(false);
            setDeletePlanId(null);
        } catch (err) {
            console.error('Error deleting plan:', err);
            setError(err instanceof Error ? err.message : 'Failed to delete plan');
        } finally {
            setDeleting(false);
        }
    };

    const handleRefresh = () => {
        fetchPlans();
    };

    const calculateProgress = (plan: APIPlanRead) => {
        const totalCourses = plan.courses.length;
        const scheduledCourses = Object.values(plan.course_dates).flat().length;
        const completedPercentage = totalCourses > 0 ? Math.round((scheduledCourses / totalCourses) * 100) : 0;
        return {
            scheduled: scheduledCourses,
            total: totalCourses,
            percentage: completedPercentage
        };
    };

    const getEndYear = (plan: APIPlanRead) => {
        if (plan.end_year) return plan.end_year;

        // Calculate end year from course_dates if not explicitly set
        const years = Object.keys(plan.course_dates)
            .map(key => parseInt(key.split(',')[0]))
            .filter(year => !isNaN(year));

        return years.length > 0 ? Math.max(...years) : plan.start_year;
    };

    if (loading) {
        return (
            <main className="max-w-7xl mx-auto px-8 mt-4">
                <h1 className="text-2xl font-bold mb-6">Your Plans</h1>
                <div className="text-center p-8">
                    <p>Loading your plans...</p>
                </div>
            </main>
        );
    }

    if (error) {
        return (
            <main className="max-w-7xl mx-auto px-8 mt-4">
                <h1 className="text-2xl font-bold mb-6">Your Plans</h1>
                <div className="text-center p-8 bg-red-50 rounded-lg">
                    <p className="text-red-600 mb-4">Error: {error}</p>
                    <Button onClick={handleRefresh} accent>
                        Try Again
                    </Button>
                </div>
            </main>
        );
    }

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
                            className="mt-4 px-4 py-2 text-white rounded "
                        >
                            Create Your First Plan
                        </Button>
                    </div>
                )}

                <ul className="space-y-4">
                    {plans.map((plan) => {
                        const progress = calculateProgress(plan);
                        const endYear = getEndYear(plan);

                        return (
                            <li key={plan.plan_id} className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                                <div className="p-4 bg-white">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h2 className="text-xl font-semibold">{plan.name}</h2>
                                            <div className="text-sm text-gray-500 mt-1">
                                                <span className="">Degree: {plan.degree.title}</span>
                                            </div>
                                            <div className="text-sm mt-2">
                                                <span>
                                                    {plan.start_year} Semester {plan.start_sem} to {endYear}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="flex space-x-2">
                                            <Button
                                                onClick={() => {
                                                    router.push(`/plan/${plan.plan_id}`);
                                                }}
                                                accent
                                                className="px-3 py-1"
                                            >
                                                Open Plan
                                            </Button>
                                            <Button
                                                onClick={handleRefresh}
                                                disabled={loading}
                                                className="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300 disabled:opacity-50"
                                            >
                                                {loading ? 'Refreshing...' : 'Refresh'}
                                            </Button>
                                            <Dropdown>
                                                <DropdownButton icon>
                                                    <EllipsisVerticalIcon />
                                                </DropdownButton>
                                                <DropdownMenu>
                                                    <DropdownItem
                                                        onClick={() => {
                                                            setDeletePlanId(plan.plan_id);
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

                                    <div className="mt-4">
                                        <div className="flex justify-between text-sm mb-1">
                                            <span>Courses Scheduled: {progress.scheduled} of {progress.total}</span>
                                            <span>{progress.percentage}% Scheduled</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                                            <div
                                                className="bg-blue-600 h-2.5 rounded-full"
                                                style={{ width: `${progress.percentage}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                </div>
                            </li>
                        );
                    })}
                </ul>
            </main>

            <Dialog
                open={isDeleteOpen}
                onClose={(open: boolean) => {
                    setIsDeleteOpen(open);
                    if (!open) setDeletePlanId(null);
                }}
            >
                <DialogTitle>Delete plan</DialogTitle>
                <DialogDescription>Are you sure you want to delete this plan? This action cannot be undone.</DialogDescription>
                <DialogBody>
                    <p className="text-sm text-gray-600">This will permanently remove the selected plan.</p>
                </DialogBody>
                <DialogActions>
                    <Button
                        onClick={() => { setIsDeleteOpen(false); setDeletePlanId(null); }}
                        outline
                        disabled={deleting}
                    >
                        Cancel
                    </Button>
                    <Button
                        onClick={() => handleDelete(deletePlanId)}
                        accent
                        disabled={deleting}
                    >
                        {deleting ? 'Deleting...' : 'Delete'}
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
}
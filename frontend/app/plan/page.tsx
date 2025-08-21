import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/button";
import { Dropdown, DropdownButton, DropdownItem, DropdownMenu } from "@/components/dropdown";
import { EllipsisVerticalIcon } from "@heroicons/react/16/solid";
import { Dialog, DialogActions, DialogBody, DialogDescription, DialogTitle } from "@/components/dialog";
import { APIPlanRead } from "@/app/api/plan/types";
import { Suspense } from 'react'
import Plans from "./plans";

export default async function PlanPage() {
    const plans: Promise<APIPlanRead[]> = fetch('/api/plan')
        .then((res) => {
            if (!res.ok) throw new Error(`Failed to fetch plans: ${res.status}`);
            return res.json() as Promise<APIPlanRead[]>;
        });

    return (
        <div className="max-w-7xl mx-auto px-8 my-4">
            <h1 className="text-2xl font-bold mb-6">Your Plans</h1>
            <Suspense fallback={<div>Loading...</div>}>
                <Plans plans={plans}/>
            </Suspense>
        </div>
    );
}
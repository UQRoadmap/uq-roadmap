'use client'
import { use } from 'react'
import { APIPlanRead } from '../api/plan/types';
 

export default function Plans({plans}: {plans: Promise<APIPlanRead[]>}) {
    const userPlans = use(plans);

    return (
        <div>
            
        </div>
    )
}
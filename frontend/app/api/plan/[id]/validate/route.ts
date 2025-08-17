
// cspell:disable

import { NextRequest, NextResponse } from "next/server"
import { BACKEND_BASE_URL } from "../../../common";


const data = [
  {
    "status": 2,
    "percentage": 0,
    "message": "0 units found in plan, but 8 required. Add from: ENGG1100",
    "relevant": [
      "ENGG1100"
    ]
  },
  {
    "status": 2,
    "percentage": null,
    "message": "No Field of Study found in plan. Add from: CHEMIX2350, CBIOMX2350, CBIOPX2350, CHENVX2350, CHMETX2350, CIVENX2350, CIENVX2350, ELENGX2350, ELEBEX2350, ELECEX2350, MECENX2350, MECAEX2350, MECMEX2350, MECTRX2350, SOFTEX2350",
    "relevant": [
      "CHEMIX2350",
      "CBIOMX2350",
      "CBIOPX2350",
      "CHENVX2350",
      "CHMETX2350",
      "CIVENX2350",
      "CIENVX2350",
      "ELENGX2350",
      "ELEBEX2350",
      "ELECEX2350",
      "MECENX2350",
      "MECAEX2350",
      "MECMEX2350",
      "MECTRX2350",
      "SOFTEX2350"
    ]
  },
  {
    "status": 0,
    "percentage": 100,
    "message": "Complete 0 to 4 units from the following ['CHEM1090', 'PHYS1171', 'MATH1050']",
    "relevant": [
      "CHEM1090",
      "PHYS1171",
      "MATH1050"
    ]
  },
  {
    "status": 0,
    "percentage": 100,
    "message": "Complete 0 to 4 units from the following ['BIOE1001', 'BIOL1040', 'CHEM1100', 'DSGN1500', 'ERTH1501', 'ENGG2000', 'PHYS1002']",
    "relevant": [
      "BIOE1001",
      "BIOL1040",
      "CHEM1100",
      "DSGN1500",
      "ERTH1501",
      "ENGG2000",
      "PHYS1002"
    ]
  },
  {
    "status": 0,
    "percentage": 100,
    "message": "Complete 0 to 6 units from the following []",
    "relevant": []
  },
  {
    "status": 0,
    "percentage": 100,
    "message": "Complete 0 to 6 units from the following []",
    "relevant": []
  }
]

export async function GET(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
    const { id } = await params

    try {
        //Fetch live data from backend. `no-store` ensures we always get fresh data.
        // const res = await fetch(`${BACKEND_BASE_URL}/plan/${id}/validate`, {
        //     method: "PUT",
        //     headers: { "Accept": "application/json" },
        //     cache: "no-store"
        // });

        // if (res.status === 404) {
        //     console.debug(`Couldn't find plan under id: ${id}`);
        //     return NextResponse.json({});
        // }

        // if (!res.ok) {
        //     const errorText = await res.text();
        //     return NextResponse.json(
        //         { error: errorText || `Failed to fetch validation for plan ${id}` },
        //         { status: res.status }
        //     );
        // }

        // const plan = await res.json();
        // return NextResponse.json(plan);
        return NextResponse.json(data);
    } catch (err) {
        console.error(err);
        return NextResponse.json({ error: "Internal server error" }, { status: 500 });
    }
}

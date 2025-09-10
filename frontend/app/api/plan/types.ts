export interface APIPlanCreateUpdate {
  degree_id: string; // UUID as string
  name: string;

  start_year: number;
  end_year: number;
  start_sem: 1 | 2;

  // maps (year, sem) -> course_codes e.g., 'CSSE2310'
  course_dates_input: Record<string, string[]>;
  // key is stringified tuple "year,sem"

  // maps (part) -> course_code list
  course_reqs: Record<string, string[]>;

  // maps (part) -> degree code (e.g., "2525")
  specialisations: Record<string, string[]>;
}

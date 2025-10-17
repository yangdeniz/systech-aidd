import { getStats } from "@/lib/api";
import type { Period } from "@/types/api";
import { useQuery } from "@tanstack/react-query";

export function useStats(period: Period) {
  return useQuery({
    queryKey: ["stats", period],
    queryFn: () => getStats(period),
  });
}

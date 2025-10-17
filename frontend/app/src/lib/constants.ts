export const PERIODS = {
  DAY: "day" as const,
  WEEK: "week" as const,
  MONTH: "month" as const,
};

export const DEFAULT_PERIOD = PERIODS.WEEK;

export const API_CACHE_TIME = 60 * 1000; // 1 minute

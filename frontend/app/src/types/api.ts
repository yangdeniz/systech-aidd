export interface MetricCard {
  title: string;
  value: string | number;
  change_percent: number;
  description: string;
}

export interface TimeSeriesPoint {
  date: string; // ISO format
  value: number;
}

export interface DialogueInfo {
  user_id: number;
  username: string | null;
  message_count: number;
  last_message_at: string; // ISO datetime
}

export interface TopUser {
  user_id: number;
  username: string | null;
  total_messages: number;
  dialogue_count: number;
}

export interface StatsResponse {
  metrics: MetricCard[];
  time_series: TimeSeriesPoint[];
  recent_dialogues: DialogueInfo[];
  top_users: TopUser[];
}

export type Period = "day" | "week" | "month";

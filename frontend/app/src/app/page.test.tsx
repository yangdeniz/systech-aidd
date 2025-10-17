import * as api from "@/lib/api";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import HomePage from "./page";

// Mock the API
jest.mock("@/lib/api");
const mockedApi = api as jest.Mocked<typeof api>;

// Mock next-themes
jest.mock("next-themes", () => ({
  useTheme: () => ({ setTheme: jest.fn() }),
}));

const mockStatsData = {
  metrics: [
    {
      title: "Total Dialogues",
      value: 1234,
      change_percent: 12.5,
      description: "Up from last period",
    },
    {
      title: "Active Users",
      value: 567,
      change_percent: -5.2,
      description: "Down from last period",
    },
    {
      title: "Avg Messages per Dialogue",
      value: 45.7,
      change_percent: 8.3,
      description: "Increased engagement",
    },
    {
      title: "Messages Today",
      value: 892,
      change_percent: 15.0,
      description: "Strong activity",
    },
  ],
  time_series: [
    { date: "2024-10-15T00:00:00Z", value: 120 },
    { date: "2024-10-16T00:00:00Z", value: 150 },
    { date: "2024-10-17T00:00:00Z", value: 180 },
  ],
  recent_dialogues: [
    {
      user_id: 123456,
      username: "test_user",
      message_count: 10,
      last_message_at: "2024-10-17T14:30:00Z",
    },
  ],
  top_users: [
    {
      user_id: 123456,
      username: "top_user",
      total_messages: 250,
      dialogue_count: 10,
    },
  ],
};

describe("HomePage", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    mockedApi.getStats.mockResolvedValue(mockStatsData);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders dashboard title", async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <HomePage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Dashboard")).toBeInTheDocument();
    });
  });

  it("renders all metric cards", async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <HomePage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Total Dialogues")).toBeInTheDocument();
      expect(screen.getByText("Active Users")).toBeInTheDocument();
      expect(screen.getByText("Avg Messages per Dialogue")).toBeInTheDocument();
      expect(screen.getByText("Messages Today")).toBeInTheDocument();
    });
  });

  it("renders activity chart", async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <HomePage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Activity Overview")).toBeInTheDocument();
    });
  });

  it("renders recent dialogues section", async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <HomePage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Recent Dialogues")).toBeInTheDocument();
      expect(screen.getByText("test_user")).toBeInTheDocument();
    });
  });

  it("renders top users section", async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <HomePage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Top Users")).toBeInTheDocument();
      expect(screen.getByText("top_user")).toBeInTheDocument();
    });
  });

  it("switches period and fetches new data", async () => {
    const user = userEvent.setup();

    render(
      <QueryClientProvider client={queryClient}>
        <HomePage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Dashboard")).toBeInTheDocument();
    });

    // Click on Day tab
    const dayTab = screen.getByRole("tab", { name: "Day" });
    await user.click(dayTab);

    await waitFor(() => {
      expect(mockedApi.getStats).toHaveBeenCalledWith("day");
    });
  });

  it("displays loading state", () => {
    // Create a query client with infinite loading
    const loadingQueryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    mockedApi.getStats.mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(
      <QueryClientProvider client={loadingQueryClient}>
        <HomePage />
      </QueryClientProvider>
    );

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("displays error state", async () => {
    mockedApi.getStats.mockRejectedValue(new Error("API Error"));

    render(
      <QueryClientProvider client={queryClient}>
        <HomePage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Error loading stats/i)).toBeInTheDocument();
    });
  });
});

import { AuthProvider } from "@/contexts/AuthContext";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { useRouter } from "next/navigation";
import HomePage from "./page";

// Mock next/navigation
jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
}));

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, "localStorage", {
  value: localStorageMock,
});

// Mock fetch
global.fetch = jest.fn();

const mockPush = jest.fn();

// Helper function to render with all required providers
const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{component}</AuthProvider>
    </QueryClientProvider>
  );
};

describe("HomePage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.clear();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
  });

  it("shows loading state initially", () => {
    renderWithProviders(<HomePage />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("redirects to login when not authenticated", async () => {
    renderWithProviders(<HomePage />);

    // Wait for the redirect to be called
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/login");
    });
  });

  it("redirects to admin dashboard when user is administrator", async () => {
    // Setup authenticated admin user
    const adminUser = {
      user_id: 1,
      username: "admin",
      role: "administrator",
      token: "test-token",
    };

    localStorageMock.setItem("auth_token", "test-token");
    localStorageMock.setItem("auth_user", JSON.stringify(adminUser));

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ valid: true }),
    });

    renderWithProviders(<HomePage />);

    // Wait for the redirect to be called
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/admin/dashboard");
    });
  });

  it("redirects to user chat when user is regular user", async () => {
    // Setup authenticated regular user
    const regularUser = {
      user_id: 2,
      username: "user",
      role: "user",
      token: "test-token",
    };

    localStorageMock.setItem("auth_token", "test-token");
    localStorageMock.setItem("auth_user", JSON.stringify(regularUser));

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ valid: true }),
    });

    renderWithProviders(<HomePage />);

    // Wait for the redirect to be called
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/user/chat");
    });
  });
});

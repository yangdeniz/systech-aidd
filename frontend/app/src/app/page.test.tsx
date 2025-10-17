import { AuthProvider } from "@/contexts/AuthContext";
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

describe("HomePage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.clear();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
  });

  it("shows loading state initially", () => {
    render(
      <AuthProvider>
        <HomePage />
      </AuthProvider>
    );

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("redirects to login when not authenticated", async () => {
    render(
      <AuthProvider>
        <HomePage />
      </AuthProvider>
    );

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

    render(
      <AuthProvider>
        <HomePage />
      </AuthProvider>
    );

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

    render(
      <AuthProvider>
        <HomePage />
      </AuthProvider>
    );

    // Wait for the redirect to be called
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/user/chat");
    });
  });
});

import { render, screen } from "@testing-library/react";
import { TopUsers } from "./TopUsers";

const mockUsers = [
  {
    user_id: 123456,
    username: "top_user",
    total_messages: 250,
    dialogue_count: 10,
  },
  {
    user_id: 789012,
    username: null,
    total_messages: 150,
    dialogue_count: 8,
  },
  {
    user_id: 345678,
    username: "active_user",
    total_messages: 100,
    dialogue_count: 5,
  },
];

describe("TopUsers", () => {
  it("renders table with top users", () => {
    render(<TopUsers users={mockUsers} />);

    expect(screen.getByText("Top Users")).toBeInTheDocument();
    expect(screen.getByText("Most active users by message count")).toBeInTheDocument();
    expect(screen.getByText("123456")).toBeInTheDocument();
    expect(screen.getByText("top_user")).toBeInTheDocument();
  });

  it("displays rank badges for users", () => {
    render(<TopUsers users={mockUsers} />);

    expect(screen.getByText("#1")).toBeInTheDocument();
    expect(screen.getByText("#2")).toBeInTheDocument();
    expect(screen.getByText("#3")).toBeInTheDocument();
  });

  it("displays Anonymous for null username", () => {
    render(<TopUsers users={mockUsers} />);

    expect(screen.getByText("Anonymous")).toBeInTheDocument();
  });

  it("displays message counts and dialogue counts", () => {
    render(<TopUsers users={mockUsers} />);

    expect(screen.getByText("250")).toBeInTheDocument();
    expect(screen.getByText("150")).toBeInTheDocument();
    expect(screen.getByText("100")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("8")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
  });

  it("shows empty state when no users", () => {
    render(<TopUsers users={[]} />);

    expect(screen.getByText("No users found")).toBeInTheDocument();
  });

  it("renders table headers", () => {
    render(<TopUsers users={mockUsers} />);

    expect(screen.getByText("Rank")).toBeInTheDocument();
    expect(screen.getByText("User ID")).toBeInTheDocument();
    expect(screen.getByText("Username")).toBeInTheDocument();
    expect(screen.getByText("Messages")).toBeInTheDocument();
    expect(screen.getByText("Dialogues")).toBeInTheDocument();
  });
});

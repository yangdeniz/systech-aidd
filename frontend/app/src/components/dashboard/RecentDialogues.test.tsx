import { render, screen } from "@testing-library/react";
import { RecentDialogues } from "./RecentDialogues";

const mockDialogues = [
  {
    user_id: 123456,
    username: "john_doe",
    message_count: 15,
    last_message_at: "2024-10-17T14:30:00Z",
  },
  {
    user_id: 789012,
    username: null,
    message_count: 8,
    last_message_at: "2024-10-17T12:00:00Z",
  },
];

describe("RecentDialogues", () => {
  it("renders table with dialogues", () => {
    render(<RecentDialogues dialogues={mockDialogues} />);

    expect(screen.getByText("Recent Dialogues")).toBeInTheDocument();
    expect(screen.getByText("Latest 10 active dialogues")).toBeInTheDocument();
    expect(screen.getByText("123456")).toBeInTheDocument();
    expect(screen.getByText("john_doe")).toBeInTheDocument();
  });

  it("displays Anonymous for null username", () => {
    render(<RecentDialogues dialogues={mockDialogues} />);

    expect(screen.getByText("Anonymous")).toBeInTheDocument();
  });

  it("formats dates correctly in yyyy-MM-dd format", () => {
    render(<RecentDialogues dialogues={mockDialogues} />);

    const dates = screen.getAllByText("2024-10-17");
    expect(dates.length).toBeGreaterThan(0);
    dates.forEach((date) => {
      expect(date).toBeInTheDocument();
    });
  });

  it("displays message counts", () => {
    render(<RecentDialogues dialogues={mockDialogues} />);

    expect(screen.getByText("15")).toBeInTheDocument();
    expect(screen.getByText("8")).toBeInTheDocument();
  });

  it("shows empty state when no dialogues", () => {
    render(<RecentDialogues dialogues={[]} />);

    expect(screen.getByText("No dialogues found")).toBeInTheDocument();
  });

  it("renders table headers", () => {
    render(<RecentDialogues dialogues={mockDialogues} />);

    expect(screen.getByText("User ID")).toBeInTheDocument();
    expect(screen.getByText("Username")).toBeInTheDocument();
    expect(screen.getByText("Messages")).toBeInTheDocument();
    expect(screen.getByText("Last Message")).toBeInTheDocument();
  });
});

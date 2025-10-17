import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ActivityChart } from "./ActivityChart";

const mockData = [
  { date: "2024-10-15T00:00:00Z", value: 120 },
  { date: "2024-10-16T00:00:00Z", value: 150 },
  { date: "2024-10-17T00:00:00Z", value: 180 },
];

describe("ActivityChart", () => {
  it("renders chart with data", () => {
    const mockOnPeriodChange = jest.fn();

    render(<ActivityChart data={mockData} period="week" onPeriodChange={mockOnPeriodChange} />);

    expect(screen.getByText("Activity Overview")).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Day" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Week" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Month" })).toBeInTheDocument();
  });

  it("displays correct active period", () => {
    const mockOnPeriodChange = jest.fn();

    render(<ActivityChart data={mockData} period="week" onPeriodChange={mockOnPeriodChange} />);

    const weekTab = screen.getByRole("tab", { name: "Week" });
    expect(weekTab).toHaveAttribute("data-state", "active");
  });

  it("calls onPeriodChange when switching periods", async () => {
    const user = userEvent.setup();
    const mockOnPeriodChange = jest.fn();

    render(<ActivityChart data={mockData} period="week" onPeriodChange={mockOnPeriodChange} />);

    const dayTab = screen.getByRole("tab", { name: "Day" });
    await user.click(dayTab);

    expect(mockOnPeriodChange).toHaveBeenCalledWith("day");
  });

  it("handles empty data gracefully", () => {
    const mockOnPeriodChange = jest.fn();

    render(<ActivityChart data={[]} period="week" onPeriodChange={mockOnPeriodChange} />);

    expect(screen.getByText("Activity Overview")).toBeInTheDocument();
  });
});

import { render, screen } from "@testing-library/react";
import { MetricCard } from "./MetricCard";

describe("MetricCard", () => {
  it("renders title, value, and description", () => {
    render(
      <MetricCard
        title="Test Metric"
        value={1234}
        change_percent={12.5}
        description="Test description"
      />
    );

    expect(screen.getByText("Test Metric")).toBeInTheDocument();
    expect(screen.getByText("1234")).toBeInTheDocument();
    expect(screen.getByText("Test description")).toBeInTheDocument();
  });

  it("displays positive trend with TrendingUp icon", () => {
    render(
      <MetricCard
        title="Test Metric"
        value={1234}
        change_percent={12.5}
        description="Trending up"
      />
    );

    expect(screen.getByText("+12.5%")).toBeInTheDocument();
    // Check for green text color class
    const percentElement = screen.getByText("+12.5%");
    expect(percentElement).toHaveClass("text-green-600");
  });

  it("displays negative trend with TrendingDown icon", () => {
    render(
      <MetricCard
        title="Test Metric"
        value={1234}
        change_percent={-5.2}
        description="Trending down"
      />
    );

    expect(screen.getByText("-5.2%")).toBeInTheDocument();
    // Check for red text color class
    const percentElement = screen.getByText("-5.2%");
    expect(percentElement).toHaveClass("text-red-600");
  });

  it("handles zero change percent correctly", () => {
    render(
      <MetricCard title="Test Metric" value={1234} change_percent={0} description="No change" />
    );

    expect(screen.getByText("+0%")).toBeInTheDocument();
    const percentElement = screen.getByText("+0%");
    expect(percentElement).toHaveClass("text-green-600");
  });

  it("renders string values correctly", () => {
    render(
      <MetricCard
        title="Test Metric"
        value="$1,234.56"
        change_percent={10}
        description="Currency value"
      />
    );

    expect(screen.getByText("$1,234.56")).toBeInTheDocument();
  });
});

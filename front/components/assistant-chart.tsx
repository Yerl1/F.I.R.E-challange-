"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3, TrendingUp, PieChart as PieIcon, AreaChart as AreaIcon } from "lucide-react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface ChartData {
  chartType: "bar" | "line" | "pie" | "area";
  title: string;
  xAxisLabel: string | null;
  yAxisLabel: string | null;
  data: { label: string; value: number; value2: number | null }[];
  series1Name: string;
  series2Name: string | null;
}

const CHART_COLORS = [
  "var(--color-chart-1)",
  "var(--color-chart-2)",
  "var(--color-chart-3)",
  "var(--color-chart-4)",
  "var(--color-chart-5)",
];

const PIE_COLORS = [
  "oklch(0.45 0.10 255)",
  "oklch(0.55 0.08 250)",
  "oklch(0.65 0.06 245)",
  "oklch(0.75 0.04 240)",
  "oklch(0.35 0.08 255)",
  "oklch(0.60 0.12 200)",
  "oklch(0.50 0.10 180)",
  "oklch(0.70 0.08 220)",
];

function getChartIcon(type: string) {
  switch (type) {
    case "bar":
      return <BarChart3 className="size-4 text-primary" />;
    case "line":
      return <TrendingUp className="size-4 text-primary" />;
    case "pie":
      return <PieIcon className="size-4 text-primary" />;
    case "area":
      return <AreaIcon className="size-4 text-primary" />;
    default:
      return <BarChart3 className="size-4 text-primary" />;
  }
}

export function AssistantChart({ data }: { data: ChartData }) {
  const { chartType, title, xAxisLabel, yAxisLabel, series1Name, series2Name } =
    data;

  const hasSecondSeries = data.data.some((d) => d.value2 !== null);

  const chartData = data.data.map((d) => ({
    name: d.label,
    [series1Name]: d.value,
    ...(hasSecondSeries && series2Name
      ? { [series2Name]: d.value2 }
      : {}),
  }));

  return (
    <Card className="overflow-hidden border-border">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm font-medium text-foreground">
          {getChartIcon(chartType)}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="pb-4">
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            {chartType === "bar" ? (
              <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 20, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11, fill: "var(--color-muted-foreground)" }}
                  label={xAxisLabel ? { value: xAxisLabel, position: "bottom", offset: 5, fontSize: 11, fill: "var(--color-muted-foreground)" } : undefined}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: "var(--color-muted-foreground)" }}
                  label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: "insideLeft", offset: 0, fontSize: 11, fill: "var(--color-muted-foreground)" } : undefined}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--color-card)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "8px",
                    fontSize: 12,
                    color: "var(--color-foreground)",
                  }}
                />
                {(hasSecondSeries || chartData.length > 0) && <Legend wrapperStyle={{ fontSize: 12 }} />}
                <Bar dataKey={series1Name} fill={CHART_COLORS[0]} radius={[4, 4, 0, 0]} />
                {hasSecondSeries && series2Name && (
                  <Bar dataKey={series2Name} fill={CHART_COLORS[1]} radius={[4, 4, 0, 0]} />
                )}
              </BarChart>
            ) : chartType === "line" ? (
              <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 20, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11, fill: "var(--color-muted-foreground)" }}
                  label={xAxisLabel ? { value: xAxisLabel, position: "bottom", offset: 5, fontSize: 11, fill: "var(--color-muted-foreground)" } : undefined}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: "var(--color-muted-foreground)" }}
                  label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: "insideLeft", offset: 0, fontSize: 11, fill: "var(--color-muted-foreground)" } : undefined}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--color-card)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "8px",
                    fontSize: 12,
                    color: "var(--color-foreground)",
                  }}
                />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Line type="monotone" dataKey={series1Name} stroke={CHART_COLORS[0]} strokeWidth={2} dot={{ r: 3 }} />
                {hasSecondSeries && series2Name && (
                  <Line type="monotone" dataKey={series2Name} stroke={CHART_COLORS[1]} strokeWidth={2} dot={{ r: 3 }} />
                )}
              </LineChart>
            ) : chartType === "area" ? (
              <AreaChart data={chartData} margin={{ top: 5, right: 20, bottom: 20, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11, fill: "var(--color-muted-foreground)" }}
                  label={xAxisLabel ? { value: xAxisLabel, position: "bottom", offset: 5, fontSize: 11, fill: "var(--color-muted-foreground)" } : undefined}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: "var(--color-muted-foreground)" }}
                  label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: "insideLeft", offset: 0, fontSize: 11, fill: "var(--color-muted-foreground)" } : undefined}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--color-card)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "8px",
                    fontSize: 12,
                    color: "var(--color-foreground)",
                  }}
                />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Area type="monotone" dataKey={series1Name} stroke={CHART_COLORS[0]} fill={CHART_COLORS[0]} fillOpacity={0.15} strokeWidth={2} />
                {hasSecondSeries && series2Name && (
                  <Area type="monotone" dataKey={series2Name} stroke={CHART_COLORS[1]} fill={CHART_COLORS[1]} fillOpacity={0.15} strokeWidth={2} />
                )}
              </AreaChart>
            ) : (
              <PieChart>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--color-card)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "8px",
                    fontSize: 12,
                    color: "var(--color-foreground)",
                  }}
                />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Pie
                  data={data.data.map((d) => ({ name: d.label, value: d.value }))}
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  innerRadius={50}
                  dataKey="value"
                  paddingAngle={2}
                  label={({ name, percent }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine={false}
                  style={{ fontSize: 11 }}
                >
                  {data.data.map((_, i) => (
                    <Cell
                      key={`cell-${i}`}
                      fill={PIE_COLORS[i % PIE_COLORS.length]}
                    />
                  ))}
                </Pie>
              </PieChart>
            )}
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

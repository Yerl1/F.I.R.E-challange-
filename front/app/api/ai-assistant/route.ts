import {
  convertToModelMessages,
  streamText,
  tool,
  UIMessage,
} from "ai";
import { z } from "zod";

export const maxDuration = 60;

const chartDataPointSchema = z.object({
  label: z.string(),
  value: z.number(),
  value2: z.number().nullable(),
});

const generateChart = tool({
  description:
    "Generate a chart to visualize data. Use this whenever the user asks for a chart, graph, visualization, or when presenting numerical/statistical data that would benefit from a visual representation. Supports bar, line, pie, and area chart types.",
  inputSchema: z.object({
    chartType: z
      .enum(["bar", "line", "pie", "area"])
      .describe("The type of chart to render"),
    title: z.string().describe("A descriptive title for the chart"),
    xAxisLabel: z.string().nullable().describe("Label for the X axis (not used for pie charts)"),
    yAxisLabel: z.string().nullable().describe("Label for the Y axis (not used for pie charts)"),
    data: z
      .array(chartDataPointSchema)
      .describe(
        "The data points for the chart. Use 'label' for category names, 'value' for primary metric, and 'value2' (nullable) for an optional second series."
      ),
    series1Name: z.string().describe("Name/legend label for the primary data series"),
    series2Name: z.string().nullable().describe("Name/legend label for the optional second data series"),
  }),
  execute: async (input) => input,
});

const generateTable = tool({
  description:
    "Generate a data table to display structured information. Use this when the user asks for tabular data, comparisons, or when data is better presented in rows and columns.",
  inputSchema: z.object({
    title: z.string().describe("A descriptive title for the table"),
    columns: z
      .array(z.string())
      .describe("Column header names"),
    rows: z
      .array(z.array(z.string()))
      .describe("Row data — each row is an array of string cell values matching the columns"),
  }),
  execute: async (input) => input,
});

export async function POST(req: Request) {
  const { messages }: { messages: UIMessage[] } = await req.json();

  const result = streamText({
    model: "openai/gpt-4.1",
    system: `You are an AI analytics assistant for Freedom Broker, a financial services company.
You help users understand data, generate charts, and provide insights about business metrics.

When asked to create charts or visualizations:
- Choose the most appropriate chart type (bar for comparisons, line for trends, pie for proportions, area for cumulative data)
- Provide realistic, well-labeled data
- Always include clear titles and axis labels
- If the user doesn't specify data, generate plausible sample data relevant to a financial broker context

When asked to show tables:
- Organize data clearly with descriptive column headers
- Keep cell values concise

You can also answer general questions about business analytics, data interpretation, and financial concepts.
Always be helpful, concise, and professional.`,
    messages: await convertToModelMessages(messages),
    tools: {
      generateChart,
      generateTable,
    },
    stopWhen: (options) => options.steps.length >= 5,
  });

  return result.toUIMessageStreamResponse();
}

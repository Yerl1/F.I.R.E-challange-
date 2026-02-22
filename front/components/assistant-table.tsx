"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Table as TableIcon } from "lucide-react";

interface TableData {
  title: string;
  columns: string[];
  rows: string[][];
}

export function AssistantTable({ data }: { data: TableData }) {
  return (
    <Card className="overflow-hidden border-border">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm font-medium text-foreground">
          <TableIcon className="size-4 text-primary" />
          {data.title}
        </CardTitle>
      </CardHeader>
      <CardContent className="pb-4">
        <div className="overflow-x-auto rounded-md border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                {data.columns.map((col, i) => (
                  <TableHead
                    key={i}
                    className="whitespace-nowrap text-xs font-semibold"
                  >
                    {col}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.rows.map((row, rowIdx) => (
                <TableRow key={rowIdx}>
                  {row.map((cell, cellIdx) => (
                    <TableCell
                      key={cellIdx}
                      className="whitespace-nowrap text-xs"
                    >
                      {cell}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

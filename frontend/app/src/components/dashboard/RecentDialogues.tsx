import { format, parseISO } from "date-fns";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { DialogueInfo } from "@/types/api";

interface RecentDialoguesProps {
  dialogues: DialogueInfo[];
}

export function RecentDialogues({ dialogues }: RecentDialoguesProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Dialogues</CardTitle>
        <CardDescription>Latest 10 active dialogues</CardDescription>
      </CardHeader>
      <CardContent>
        {dialogues.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-muted-foreground">
            No dialogues found
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="hidden sm:table-cell">User ID</TableHead>
                <TableHead>Username</TableHead>
                <TableHead className="text-right">Messages</TableHead>
                <TableHead className="text-right hidden md:table-cell">Last Message</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {dialogues.map((dialogue) => (
                <TableRow key={dialogue.user_id}>
                  <TableCell className="hidden sm:table-cell font-mono text-xs sm:text-sm">{dialogue.user_id}</TableCell>
                  <TableCell className="font-medium">
                    {dialogue.username || (
                      <span className="text-muted-foreground italic">Anonymous</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">{dialogue.message_count}</TableCell>
                  <TableCell className="text-right font-mono text-xs sm:text-sm hidden md:table-cell">
                    {format(parseISO(dialogue.last_message_at), "yyyy-MM-dd")}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

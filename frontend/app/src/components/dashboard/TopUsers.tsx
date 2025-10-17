import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { TopUser } from "@/types/api";

interface TopUsersProps {
  users: TopUser[];
}

export function TopUsers({ users }: TopUsersProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Users</CardTitle>
        <CardDescription>Most active users by message count</CardDescription>
      </CardHeader>
      <CardContent>
        {users.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-muted-foreground">
            No users found
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-16">Rank</TableHead>
                <TableHead>User ID</TableHead>
                <TableHead>Username</TableHead>
                <TableHead className="text-right">Messages</TableHead>
                <TableHead className="text-right">Dialogues</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user, index) => (
                <TableRow key={user.user_id}>
                  <TableCell>
                    <Badge variant={index === 0 ? "default" : "secondary"}>#{index + 1}</Badge>
                  </TableCell>
                  <TableCell className="font-mono">{user.user_id}</TableCell>
                  <TableCell>
                    {user.username || (
                      <span className="text-muted-foreground italic">Anonymous</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right font-medium">{user.total_messages}</TableCell>
                  <TableCell className="text-right">{user.dialogue_count}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

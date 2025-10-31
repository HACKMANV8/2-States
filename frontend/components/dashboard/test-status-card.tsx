import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface TestStatusCardProps {
  title: string;
  value: number | string;
  icon: LucideIcon;
  description?: string;
  iconColor?: string;
}

export function TestStatusCard({
  title,
  value,
  icon: Icon,
  description,
  iconColor = "text-gray-500",
}: TestStatusCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className={`h-4 w-4 ${iconColor}`} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-gray-500">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}

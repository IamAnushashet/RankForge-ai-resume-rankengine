declare module "lucide-react" {
  import type { ComponentType, SVGProps } from "react";

  export type LucideIcon = ComponentType<SVGProps<SVGSVGElement> & { size?: number | string }>;
  export const Activity: LucideIcon;
  export const BarChart3: LucideIcon;
  export const CheckCircle2: LucideIcon;
  export const Download: LucideIcon;
  export const Gauge: LucideIcon;
  export const LayoutDashboard: LucideIcon;
  export const ListOrdered: LucideIcon;
  export const Play: LucideIcon;
  export const Search: LucideIcon;
  export const ShieldCheck: LucideIcon;
  export const Sparkles: LucideIcon;
  export const UserRoundSearch: LucideIcon;
}

import { PublicNav } from "@/components/public-nav";

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <PublicNav />
      <main>{children}</main>
    </div>
  );
}

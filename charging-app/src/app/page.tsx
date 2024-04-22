import Link from "next/link";
import { AvailableList } from "@/components/AvailableList";
import Admin from "@/pages/admin";

export default function Page() {
  return (
    <div className="container mx-auto">
      <div className="flex justify-center mt-6">
        <Link href="/admin">
          <div className="btn btn-primary">Admin</div>
        </Link>
      </div>
      <AvailableList />
    </div>
  );
}

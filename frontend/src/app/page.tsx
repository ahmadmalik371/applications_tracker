import { redirect } from "next/navigation";

export default function Home() {
  // Require login before accessing the portal
  redirect("/login");
}

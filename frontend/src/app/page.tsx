import { redirect } from "next/navigation";

export default function Home() {
  // Public-facing landing page redirects to job board
  redirect("/jobs");
}

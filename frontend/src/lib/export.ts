import apiClient from "./api-client";

/**
 * Download a file from the API.
 * Uses the apiClient so auth tokens are automatically attached.
 */
export async function downloadExport(
  endpoint: string,
  filename: string,
  format: "csv" | "json" = "csv"
): Promise<void> {
  const res = await apiClient.get(endpoint, {
    params: { fmt: format },
    responseType: "blob",
  });

  const blob = new Blob([res.data], {
    type: format === "csv" ? "text/csv" : "application/json",
  });

  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${filename}.${format}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

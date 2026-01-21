"use client";

import { ExternalLink } from "lucide-react";
import { Button } from "@/src/components/ui/button";

interface ExternalLinkButtonProps {
  url: string;
  label: string;
}

export function ExternalLinkButton({ url, label }: ExternalLinkButtonProps) {
  return (
    <Button
      variant="outline"
      onClick={() => window.open(url, "_blank", "noopener,noreferrer")}
      className="gap-2"
    >
      <ExternalLink className="h-4 w-4" />
      {label}
    </Button>
  );
}

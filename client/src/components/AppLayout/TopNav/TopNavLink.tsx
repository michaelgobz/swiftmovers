import { ArrowLeftIcon, Button, sprinkles } from "@swiftmovers/macaw-ui/next";
import React from "react";
import { Link } from "react-router-dom";

export const TopNavLink: React.FC<{
  to: string;
  variant?: "secondary" | "tertiary";
}> = ({ to, variant = "secondary" }) => (
  <Link to={to} className={sprinkles({ marginRight: 5 })}>
    <Button
      icon={<ArrowLeftIcon />}
      variant={variant}
      size="large"
      data-test-id="app-header-back-button"
    />
  </Link>
);

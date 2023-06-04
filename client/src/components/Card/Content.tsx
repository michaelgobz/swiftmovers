import { Box, Sprinkles } from "@swiftmovers/macaw-ui/next";
import React from "react";

export const Content: React.FC<Sprinkles> = ({ children, ...rest }) => (
  <Box paddingX={9} {...rest}>
    {children}
  </Box>
);

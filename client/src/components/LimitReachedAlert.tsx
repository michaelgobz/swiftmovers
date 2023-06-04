import { Alert, AlertProps } from "@swiftmovers/macaw-ui";
import { sprinkles } from "@swiftmovers/macaw-ui/next";
import clsx from "clsx";
import React from "react";

export type LimitReachedAlertProps = Omit<AlertProps, "variant" | "close">;

const LimitReachedAlert: React.FC<LimitReachedAlertProps> = props => (
  // TODO: migrate to new macaw-ui alert
  <Alert
    variant="warning"
    close
    className={clsx(
      sprinkles({
        gridColumn: "8",
        marginBottom: 5,
      }),
      "remove-icon-background",
    )}
    {...props}
  />
);

LimitReachedAlert.displayName = "LimitReachedAlert";
export default LimitReachedAlert;

import { makeStyles } from "@swiftmovers/macaw-ui";
import { vars } from "@swiftmovers/macaw-ui/next";

export const useAlertStyles = makeStyles(
  theme => ({
    root: {
      marginBottom: theme.spacing(3),
      "& .MuiCardContent-root": {
        backgroundColor: "unset",
        paddingRight: vars.space[11],
      },
    },
  }),
  { name: "OrderDraftAlert" },
);

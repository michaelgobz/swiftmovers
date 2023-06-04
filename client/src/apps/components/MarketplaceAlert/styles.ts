import { makeStyles } from "@swiftmovers/macaw-ui";

export const useStyles = makeStyles(
  theme => ({
    alert: {
      margin: theme.spacing(6, 0, 12, 0),
    },
  }),
  { name: "MarketplaceAlert" },
);

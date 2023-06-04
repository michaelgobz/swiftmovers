import { makeStyles } from "@swiftmovers/macaw-ui";

export const useStyles = makeStyles(
  theme => ({
    grid: {
      display: "grid",
      gridColumnGap: theme.spacing(2),
      gridTemplateColumns: "1fr 1fr",
    },
  }),
  {
    name: "OrderWeight",
  },
);

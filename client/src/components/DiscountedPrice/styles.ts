import { makeStyles } from "@swiftmovers/macaw-ui";

export const useStyles = makeStyles(
  theme => ({
    strike: {
      textDecoration: "line-through",
      color: theme.palette.grey[400],
      fontSize: "smaller",
    },
  }),
  { name: "DiscountedPrice" },
);

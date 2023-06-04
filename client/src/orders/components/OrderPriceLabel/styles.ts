import { makeStyles } from "@swiftmovers/macaw-ui";

export const useStyles = makeStyles(
  () => ({
    percentDiscountLabelContainer: {
      display: "flex",
      flexDirection: "column",
      alignItems: "flex-end",
      justifyContent: "flex-end",
    },
  }),
  { name: "OrderPriceLabel" },
);

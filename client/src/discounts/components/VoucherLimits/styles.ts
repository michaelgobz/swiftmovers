import { makeStyles } from "@swiftmovers/macaw-ui";

export const useStyles = makeStyles(
  () => ({
    cardContent: {
      display: "flex",
      flexDirection: "column",
    },
    usesLeftLabelWrapper: {
      display: "flex",
      flexDirection: "column",
      flex: 1,
    },
  }),
  { name: "VoucherLimits" },
);

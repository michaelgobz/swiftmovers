import { makeStyles } from "@swiftmovers/macaw-ui";

export const useStyles = makeStyles(
  theme => ({
    clickable: {
      cursor: "pointer",
    },
    ellipsis: {
      textOverflow: "ellipsis",
      overflow: "hidden",
    },
    tableRow: {
      minHeight: "48px",
      "&::after": {
        display: "none",
      },
    },
    selected: {
      "&&&:before": {
        display: "visible",
        position: "absolute",
        left: 0,
        width: "4px",
        height: "100%",
        backgroundColor: theme.palette.swiftmovers.active[1],
      },
    },
  }),
  { name: "TaxChannelsMenu" },
);

import { makeStyles } from "@swiftmovers/macaw-ui";

const useStyles = makeStyles(
  {
    ellipsis: {
      overflow: "hidden",
      whiteSpace: "nowrap",
      textOverflow: "ellipsis",
    },
  },
  { name: "SaleSummary" },
);

export default useStyles;

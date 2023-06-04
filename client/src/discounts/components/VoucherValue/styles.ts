import { makeStyles } from "@swiftmovers/macaw-ui";

export const useStyles = makeStyles(
  theme => ({
    colName: {
      fontSize: 14,
      paddingLeft: 0,
      width: "auto",
    },
    colPrice: {
      minWidth: 300,
    },
    colType: {
      fontSize: 14,
      textAlign: "right",
      width: 300,
    },
    table: {
      tableLayout: "fixed",
    },
    tableContainer: {
      margin: theme.spacing(0, -4),
    },
  }),
  {
    name: "VoucherValue",
  },
);

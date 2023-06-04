import { makeStyles } from "@swiftmovers/macaw-ui";

const useStyles = makeStyles(
  theme => ({
    note: {
      marginTop: theme.spacing(3),
    },
  }),
  { name: "GiftCardExportDialogContent" },
);

export default useStyles;

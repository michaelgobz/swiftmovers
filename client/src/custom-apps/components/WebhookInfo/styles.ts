import { makeStyles } from "@swiftmovers/macaw-ui";

export const useStyles = makeStyles(
  theme => ({
    toolbar: {
      padding: theme.spacing(2),
      backgroundColor: theme.palette.swiftmovers.fail.mid,
      color: theme.palette.common.black,
      marginBottom: theme.spacing(2),
    },
    cardTitle: {
      paddingLeft: 0,
    },
    card: {
      paddingLeft: 0,
    },
  }),
  { name: "WebhookInfo" },
);

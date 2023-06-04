import { makeStyles } from "@swiftmovers/macaw-ui";
import { vars } from "@swiftmovers/macaw-ui/next";

const useStyles = makeStyles(
  {
    header: {
      fontWeight: 500,
      marginBottom: vars.space[1],
    },
    root: {
      marginTop: vars.space[4],
      paddingLeft: vars.space[9],
      paddingRight: vars.space[9],
    },
  },
  { name: "GiftCardHistory" },
);

export default useStyles;

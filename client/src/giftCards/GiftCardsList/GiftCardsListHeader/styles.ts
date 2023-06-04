import { makeStyles } from "@swiftmovers/macaw-ui";

const useStyles = makeStyles(
  theme => ({
    preview: {
      position: "absolute",
      top: theme.spacing(-4),
    },
    title: {
      position: "relative",
    },
  }),
  { name: "GiftCardListHeader" },
);

export default useStyles;

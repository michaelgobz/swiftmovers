import { makeStyles } from "@swiftmovers/macaw-ui";

const useStyles = makeStyles(
  theme => ({
    andLabel: {
      margin: theme.spacing(0, 2),
    },
    arrow: {
      marginRight: theme.spacing(2),
    },
    filterSettings: {
      padding: theme.spacing(2, 3),
    },
    inputRange: {
      alignItems: "center",
      display: "flex",
    },

    option: {
      left: theme.spacing(-0.5),
      position: "relative",
    },
    optionRadio: {
      left: theme.spacing(-0.25),
    },

    fieldInput: {
      padding: "12px 0 9px 12px",
    },
  }),
  { name: "Filter" },
);

export default useStyles;

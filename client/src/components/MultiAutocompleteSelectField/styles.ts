import { alpha } from "@material-ui/core/styles";
import { makeStyles } from "@swiftmovers/macaw-ui";

export const useStyles = makeStyles(
  theme => ({
    chip: {
      width: "100%",
    },
    chipClose: {
      height: 32,
      padding: 0,
      width: 32,
      border: 0,
    },
    chipContainer: {
      display: "flex",
      flexDirection: "column",
      marginTop: theme.spacing(1),
    },
    chipInner: {
      "& svg": {
        color: theme.palette.primary.contrastText,
      },
      alignItems: "center",
      background:
        theme.palette.type === "dark"
          ? theme.palette.secondary.main
          : alpha(theme.palette.primary.main, 0.8),
      borderRadius: 18,
      color: theme.palette.primary.contrastText,
      display: "flex",
      justifyContent: "space-between",
      margin: theme.spacing(1, 0),
      paddingLeft: theme.spacing(2),
      paddingRight: theme.spacing(1),
    },
    chipLabel: {
      color: theme.palette.primary.contrastText,
    },
    container: {
      flexGrow: 1,
      position: "relative",
    },
    disabledChipInner: {
      "& svg": {
        color: theme.palette.grey[200],
      },
      alignItems: "center",
      background: alpha(theme.palette.grey[400], 0.8),
      borderRadius: 18,
      color: theme.palette.primary.contrastText,
      display: "flex",
      justifyContent: "space-between",
      margin: theme.spacing(1, 0),
      paddingLeft: theme.spacing(2),
      paddingRight: theme.spacing(1),
    },
    adornment: {
      color: theme.palette.swiftmovers.main[3],
      cursor: "pointer",
      userSelect: "none",
      display: "flex",
      alignItems: "center",
      "& svg": {
        transition: theme.transitions.duration.shorter + "ms",
      },
    },
    adornmentRotate: {
      "& svg": {
        transform: "rotate(180deg)",
      },
    },
  }),
  { name: "MultiAutocompleteSelectField" },
);

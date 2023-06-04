import { makeStyles } from "@swiftmovers/macaw-ui";

export const useSubmitCardStyles = makeStyles(
  theme => ({
    submitButtonWrapper: {
      display: "flex",
      justifyContent: "flex-end",
      marginTop: theme.spacing(1),
    },
  }),
  { name: "SubmitCard" },
);

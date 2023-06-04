import { makeStyles } from "@swiftmovers/macaw-ui";

export const useStyles = makeStyles(
  theme => ({
    installButton: {
      marginLeft: theme.spacing(2),
      height: 52,
    },
  }),
  {
    name: "InstallWithManifestFormButton",
  },
);

import { makeStyles } from "@swiftmovers/macaw-ui";

const useStyles = makeStyles(
  () => ({
    noOverflow: {
      "&&": {
        overflow: "visible",
      },
    },
  }),
  { name: "StaffDetailsPage" },
);

export default useStyles;

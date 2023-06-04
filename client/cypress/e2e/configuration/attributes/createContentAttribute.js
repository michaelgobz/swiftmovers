/// <reference types="cypress"/>
/// <reference types="../../../support"/>

import faker from "faker";

import { ATTRIBUTES_DETAILS } from "../../../elements/attribute/attributes_details";
import { ATTRIBUTES_LIST } from "../../../elements/attribute/attributes_list";
import { urlList } from "../../../fixtures/urlList";
import { getAttribute } from "../../../support/api/requests/Attribute";
import { deleteAttributesStartsWith } from "../../../support/api/utils/attributes/attributeUtils";
import { expectCorrectDataInAttribute } from "../../../support/api/utils/attributes/checkAttributeData";
import { createAttributeWithInputType } from "../../../support/pages/attributesPage";

describe("As an admin I want to create content attribute", () => {
  const startsWith = "AttrCont";
  const attributesTypes = [
    { type: "DROPDOWN", testCase: "swiftmovers_0512" },
    { type: "MULTISELECT", testCase: "swiftmovers_0513" },
    { type: "FILE", testCase: "swiftmovers_0514" },
    { type: "RICH_TEXT", testCase: "swiftmovers_0515" },
    { type: "BOOLEAN", testCase: "swiftmovers_0516" },
    { type: "DATE", testCase: "swiftmovers_0527" },
    { type: "DATE_TIME", testCase: "swiftmovers_0528" },
  ];
  const attributeReferenceType = [
    { type: "PRODUCT", testCase: "swiftmovers_0517" },
    { type: "PAGE", testCase: "swiftmovers_0518" },
    { type: "PRODUCT_VARIANT", testCase: "swiftmovers_0539" },
  ];
  const attributeNumericType = [
    {
      unitSystem: "IMPERIAL",
      unitsOf: "DISTANCE",
      unit: "FT",
      testCase: "swiftmovers_0519",
    },
    {
      unitSystem: "METRIC",
      unitsOf: "VOLUME",
      unit: "CUBIC_CENTIMETER",
      testCase: "swiftmovers_0520",
    },
    { unitSystem: "without selecting unit", testCase: "swiftmovers_0521" },
  ];

  before(() => {
    cy.clearSessionData().loginUserViaRequest();
    deleteAttributesStartsWith(startsWith);
  });

  beforeEach(() => {
    cy.clearSessionData()
      .loginUserViaRequest()
      .visit(urlList.attributes)
      .get(ATTRIBUTES_LIST.createAttributeButton)
      .click()
      .get(ATTRIBUTES_DETAILS.pageTypeAttributeCheckbox)
      .click();
  });

  attributesTypes.forEach(attributeType => {
    it(
      `should be able to create ${attributeType.type} attribute. TC:${attributeType.testCase}`,
      { tags: ["@attribute", "@allEnv", "@stable"] },
      () => {
        const attributeName = `${startsWith}${faker.datatype.number()}`;
        createAttributeWithInputType({
          name: attributeName,
          attributeType: attributeType.type,
        })
          .then(({ attribute }) => {
            getAttribute(attribute.id);
          })
          .then(attribute => {
            expectCorrectDataInAttribute(attribute, {
              attributeName,
              attributeType: attributeType.type,
            });
          });
      },
    );
  });

  attributeReferenceType.forEach(entityType => {
    it(
      `should be able to create reference to ${entityType.type} attribute. TC:${entityType.testCase}`,
      { tags: ["@attribute", "@allEnv", "@stable"] },
      () => {
        const attributeType = "REFERENCE";
        const attributeName = `${startsWith}${faker.datatype.number()}`;
        createAttributeWithInputType({
          name: attributeName,
          attributeType,
          entityType: entityType.type,
        })
          .then(({ attribute }) => {
            getAttribute(attribute.id);
          })
          .then(attribute => {
            expectCorrectDataInAttribute(attribute, {
              attributeName,
              attributeType,
              entityType: entityType.type,
            });
          });
      },
    );
  });

  attributeNumericType.forEach(numericSystemType => {
    it(
      `should be able to create numeric ${numericSystemType.unitSystem} attribute. TC: ${numericSystemType.testCase}`,
      { tags: ["@attribute", "@allEnv", "@stable"] },
      () => {
        const attributeType = "NUMERIC";
        const attributeName = `${startsWith}${faker.datatype.number()}`;
        createAttributeWithInputType({
          name: attributeName,
          attributeType,
          numericSystemType,
        })
          .then(({ attribute }) => {
            getAttribute(attribute.id);
          })
          .then(attribute => {
            expectCorrectDataInAttribute(attribute, {
              attributeName,
              attributeType,
              unit: numericSystemType.unit,
            });
          });
      },
    );
  });

  it(
    "should be able to create attribute without require value TC:swiftmovers_0522",
    { tags: ["@attribute", "@allEnv", "@stable"] },
    () => {
      const attributeType = "BOOLEAN";
      const attributeName = `${startsWith}${faker.datatype.number()}`;
      createAttributeWithInputType({
        name: attributeName,
        attributeType,
        valueRequired: false,
      })
        .then(({ attribute }) => {
          getAttribute(attribute.id);
        })
        .then(attribute => {
          expectCorrectDataInAttribute(attribute, {
            attributeName,
            attributeType,
            valueRequired: false,
          });
        });
    },
  );
});

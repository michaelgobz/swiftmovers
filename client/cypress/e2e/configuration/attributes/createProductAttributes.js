/// <reference types="cypress"/>
/// <reference types="../../../support"/>

import faker from "faker";

import { ATTRIBUTES_DETAILS } from "../../../elements/attribute/attributes_details";
import { ATTRIBUTES_LIST } from "../../../elements/attribute/attributes_list";
import { BUTTON_SELECTORS } from "../../../elements/shared/button-selectors";
import { attributeDetailsUrl, urlList } from "../../../fixtures/urlList";
import {
  createAttribute,
  getAttribute,
} from "../../../support/api/requests/Attribute";
import { deleteAttributesStartsWith } from "../../../support/api/utils/attributes/attributeUtils";
import { expectCorrectDataInAttribute } from "../../../support/api/utils/attributes/checkAttributeData";
import {
  createAttributeWithInputType,
  fillUpAttributeNameAndCode,
} from "../../../support/pages/attributesPage";

describe("As an admin I want to create product attribute", () => {
  const startsWith = "AttrCreate";
  const attributesTypes = [
    { type: "DROPDOWN", testCase: "swiftmovers_0501" },
    { type: "MULTISELECT", testCase: "swiftmovers_0502" },
    { type: "FILE", testCase: "swiftmovers_0503" },
    { type: "RICH_TEXT", testCase: "swiftmovers_0504" },
    { type: "BOOLEAN", testCase: "swiftmovers_0505" },
    { type: "DATE", testCase: "swiftmovers_0523" },
    { type: "DATE_TIME", testCase: "swiftmovers_0524" },
  ];
  const attributeReferenceType = [
    { type: "PRODUCT", testCase: "swiftmovers_0506" },
    { type: "PAGE", testCase: "swiftmovers_0507" },
    { type: "PRODUCT_VARIANT", testCase: "swiftmovers_0539" },
  ];
  const attributeNumericType = [
    {
      unitSystem: "IMPERIAL",
      unitsOf: "DISTANCE",
      unit: "FT",
      testCase: "swiftmovers_0508",
    },
    {
      unitSystem: "METRIC",
      unitsOf: "VOLUME",
      unit: "CUBIC_CENTIMETER",
      testCase: "swiftmovers_0509",
    },
    { unitSystem: "without selecting unit", testCase: "swiftmovers_0510" },
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
      .click();
  });

  attributesTypes.forEach(attributeType => {
    it(
      `should be able to create ${attributeType.type} attribute. TC:${attributeType.testCase}`,
      { tags: ["@attribute", "@allEnv", "@stable", "@oldRelease"] },
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
      `should be able to create ${entityType.type} attribute. TC:${entityType.testCase}`,
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
      `should be able to create numeric ${numericSystemType.unitSystem} attribute. TC:${numericSystemType.testCase}`,
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
    "should be able to create attribute without require value. TC:swiftmovers_0511",
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

  it(
    "should create swatch attribute. TC:swiftmovers_0531",
    { tags: ["@attribute", "@allEnv", "@stable"] },
    () => {
      const attributeType = "SWATCH";
      const attributeName = `${startsWith}${faker.datatype.number()}`;
      createAttributeWithInputType({
        name: attributeName,
        attributeType,
      })
        .then(({ attribute }) => {
          getAttribute(attribute.id);
        })
        .then(attribute => {
          expectCorrectDataInAttribute(attribute, {
            attributeName,
            attributeType,
            valueRequired: true,
          });
        });
    },
  );

  it(
    "should create swatch attribute with image. TC:swiftmovers_0532",
    { tags: ["@attribute", "@allEnv", "@stable"] },
    () => {
      const attributeType = "SWATCH";
      const attributeName = `${startsWith}${faker.datatype.number()}`;
      const swatchImage = "images/swiftmoversDemoProductSneakers.png";
      createAttributeWithInputType({
        name: attributeName,
        attributeType,
        swatchImage,
      })
        .then(({ attribute }) => {
          getAttribute(attribute.id);
        })
        .then(attribute => {
          expectCorrectDataInAttribute(attribute, {
            attributeName,
            attributeType,
            valueRequired: true,
          });
          cy.get(ATTRIBUTES_DETAILS.swatchValueImage)
            .invoke("attr", "style")
            .should("include", "swiftmoversDemoProductSneakers");
        });
    },
  );

  it(
    "should be able delete product attribute. TC:swiftmovers_0525",
    { tags: ["@attribute", "@allEnv", "@stable"] },
    () => {
      const attributeName = `${startsWith}${faker.datatype.number()}`;

      createAttribute({
        name: attributeName,
      }).then(attribute => {
        cy.visit(attributeDetailsUrl(attribute.id))
          .get(BUTTON_SELECTORS.deleteButton)
          .click()
          .addAliasToGraphRequest("AttributeDelete")
          .get(BUTTON_SELECTORS.submit)
          .click()
          .waitForRequestAndCheckIfNoErrors("@AttributeDelete");
        getAttribute(attribute.id).should("be.null");
      });
    },
  );

  it(
    "should be able update product attribute. TC:swiftmovers_0526",
    { tags: ["@attribute", "@allEnv", "@stable"] },
    () => {
      const attributeName = `${startsWith}${faker.datatype.number()}`;
      const attributeUpdatedName = `${startsWith}${faker.datatype.number()}`;

      createAttribute({
        name: attributeName,
      })
        .then(attribute => {
          cy.visit(attributeDetailsUrl(attribute.id));
          fillUpAttributeNameAndCode(attributeUpdatedName);
          cy.addAliasToGraphRequest("AttributeUpdate")
            .get(BUTTON_SELECTORS.confirm)
            .click()
            .waitForRequestAndCheckIfNoErrors("@AttributeUpdate");
          getAttribute(attribute.id);
        })
        .then(attribute => {
          expect(attribute.name).to.eq(attributeUpdatedName);
          expect(attribute.slug).to.eq(attributeUpdatedName);
        });
    },
  );
});

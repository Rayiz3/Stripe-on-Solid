import { Show, type Component, type ComponentProps } from 'solid-js'
import { style } from '@macaron-css/core';

const container = style({
    flexGrow: 1,
    height: "100%",
    paddingTop: '50px',
})

// module declaration for extending JSX elements
// to include a custom HTML element <stripe-pricing-table>
declare module "solid-js" {
    namespace JSX {
      interface IntrinsicElements {
        "stripe-pricing-table": ComponentProps<"div"> & {
          "pricing-table-id": string;
          "publishable-key": string;
        };
      }
    }
  }

// payment request for single integration for Apple pay, Google pay, Microsoft pay, etc.
const PricingTableLinks: Component<{payType: "payment" | "subscription"}> = (props) => {
    return(
      <>
        {/* if it is one-time-payment*/}
        <Show when={props.payType === "payment"}>
          <stripe-pricing-table
              class={container}
              pricing-table-id="prctbl_1Pgjc0G1Ea829cAumRKcl1OB"
              publishable-key="pk_test_51P6R0zG1Ea829cAuy7MnRyLFsQf9N5QnjLiizGw6MQFFhbX8XCQUvW3Pu7ZCkAKHOuBkuAQS6BzHk7Ya1RZk0wdV00xBvIjtaz">
          </stripe-pricing-table>
        </Show>
        
        {/* if it is subscription */}
        <Show when={props.payType === "subscription"}>
          <stripe-pricing-table
              class={container}
              pricing-table-id="prctbl_1PgGdoG1Ea829cAuivcJYiGE"
              publishable-key="pk_test_51P6R0zG1Ea829cAuy7MnRyLFsQf9N5QnjLiizGw6MQFFhbX8XCQUvW3Pu7ZCkAKHOuBkuAQS6BzHk7Ya1RZk0wdV00xBvIjtaz">
          </stripe-pricing-table>
        </Show>
      </>
    )
}

export default PricingTableLinks
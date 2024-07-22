// Customizing process :
// 1. choose theme
// 2. use variables for broad style
// 3. use rules for fine-tuning
// 4. give additional appearance using label

// for detail, see https://docs.stripe.com/elements/appearance-api?platform=web

// 1. theme
const theme: 'flat' | 'night' | 'stripe' | undefined = 'flat';

// 2. variable : CSS-like properties
const variables = {
    fontFamily: ' "Gill Sans", sans-serif',
    fontLineHeight: '1.5',
    borderRadius: '10px',
    colorBackground: '#F6F8FA',
    accessibleColorOnColorPrimary: '#262626'
};

// 3. rules : map of CSS-like selectors
const rules = {
    '.Block': {
      backgroundColor: 'var(--colorBackground)',
      boxShadow: 'none',
      padding: '12px'
    },
    '.Input': {
      padding: '12px'
    },
    '.Input:disabled, .Input--invalid:disabled': {
      color: 'lightgray'
    },
    '.Tab': {
      padding: '10px 12px 8px 12px',
      border: 'none'
    },
    '.Tab:hover': {
      border: 'none',
      boxShadow: '0px 1px 1px rgba(0, 0, 0, 0.03), 0px 3px 7px rgba(18, 42, 66, 0.04)'
    },
    '.Tab--selected, .Tab--selected:focus, .Tab--selected:hover': {
      border: 'none',
      backgroundColor: '#fff',
      boxShadow: '0 0 0 1.5px var(--colorPrimaryText), 0px 1px 1px rgba(0, 0, 0, 0.03), 0px 3px 7px rgba(18, 42, 66, 0.04)'
    },
    '.Label': {
      fontWeight: '500'
    }
  };

  // 4. labels
  const labels: "floating" | "above" | undefined = "above";

export const elementStyle = {
    theme: theme,
    variables: variables,
    rules: rules,
    labels: labels,
}
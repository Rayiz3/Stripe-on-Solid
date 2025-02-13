import type { Component } from 'solid-js'
import type { StripeLinkAuthenticationElementChangeEvent, StripeLinkAuthenticationElementOptions } from '@stripe/stripe-js'
import { createWrapper } from '../../utility/createWrapper'
import { createStripeElement } from '../../utility/createStripeElement'
import type { ElementProps } from '../../Types'

export type LinkAuthenticationElementProps = ElementProps<'linkAuthentication', StripeLinkAuthenticationElementChangeEvent & { error: undefined }> & {
  defaultValues?: StripeLinkAuthenticationElementOptions['defaultValues']
}

// e-mail form for Link authentication
const LinkAuthenticationElement: Component<LinkAuthenticationElementProps> = (props: LinkAuthenticationElementProps) => {
  const [wrapper, setWrapper] = createWrapper()

  const options = () => props.defaultValues ? { defaultValues: props.defaultValues } : {}

  createStripeElement(
    wrapper,
    'linkAuthentication',
    options,
    (type, event) => props[type]?.(event),
  );

  (LinkAuthenticationElement as any).__elementType = 'linkAuthentication'

  return <div class={props.class} ref={setWrapper} />
}

export default LinkAuthenticationElement
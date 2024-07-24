import type { Component } from 'solid-js'
import type { StripeCardCvcElementChangeEvent, StripeCardCvcElementOptions } from '@stripe/stripe-js'
import { mergeProps, splitProps } from 'solid-js'
import { createWrapper } from '../primitives/createWrapper'
import { createStripeElement } from '../primitives/createStripeElement'
import type { ElementProps } from '../Types'

export type CardCvcElementProps = ElementProps<'cardCvc', StripeCardCvcElementChangeEvent> & StripeCardCvcElementOptions

// textbox for card cvc
const CardCvc: Component<CardCvcElementProps> = (props: CardCvcElementProps) => {
  const [wrapper, setWrapper] = createWrapper()

  const defaultValues = {
    classes: {},
    style: {},
    placeholder: 'CVC',
    disabled: false,
  }
  const merged = mergeProps(defaultValues, props)
  const [options] = splitProps(merged, Object.keys(defaultValues) as Array<keyof typeof defaultValues>)

  createStripeElement(
    wrapper,
    'cardCvc',
    options,
    (type, event) => props[type]?.(event),
  );

  (CardCvc as any).__elementType = 'cardCvc'

  return <div class={props.class} ref={setWrapper} />
}

export default CardCvc
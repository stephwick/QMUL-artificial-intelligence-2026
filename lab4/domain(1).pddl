(define (domain workshop)
  (:requirements :strips :typing)

  (:types item tool location - object)

  (:predicates
    ;; where things are
    (agent-at ?l - location)
    (at ?i - item ?l - location)
    (tool-at ?t - tool ?l - location)

    ;; the one hand
    (hand-empty)
    (holding ?i - item)
    (has-tool ?t - tool)

    ;; stacking
    (on-top ?top - item ?bottom - item)   ; top rests on bottom
    (on-surface ?i - item)                 ; rests on the floor, not on another item
    (clear ?i - item)                      ; nothing on top of it

    ;; what tools can do (never change)
    (can-cut ?t - tool)
    (can-photo ?t - tool)

    ;; what has been done to an item
    (whole ?i - item)
    (cut-into-pieces ?i - item)
    (photo-taken ?i - item)
  )

  (:action walk-between-rooms
    :parameters (?from - location ?to - location)
    :precondition (and (agent-at ?from))
    :effect (and (agent-at ?to) (not (agent-at ?from)))
  )

  (:action pick-up
    :parameters (?i - item ?l - location)
    :precondition (and (agent-at ?l) (at ?i ?l) (hand-empty) (clear ?i) (on-surface ?i))
    :effect (and (holding ?i)
                 (not (hand-empty)) (not (at ?i ?l)) (not (clear ?i)) (not (on-surface ?i)))
  )

  (:action put-down
    :parameters (?i - item ?l - location)
    :precondition (and (agent-at ?l) (holding ?i))
    :effect (and (at ?i ?l) (clear ?i) (on-surface ?i) (hand-empty)
                 (not (holding ?i)))
  )

  (:action pick-up-tool
    :parameters (?t - tool ?l - location)
    :precondition (and (agent-at ?l) (tool-at ?t ?l) (hand-empty))
    :effect (and (has-tool ?t) (not (tool-at ?t ?l)) (not (hand-empty)))
  )

  (:action put-down-tool
    :parameters (?t - tool ?l - location)
    :precondition (and (agent-at ?l) (has-tool ?t))
    :effect (and (tool-at ?t ?l) (hand-empty) (not (has-tool ?t)))
  )

  (:action stack
    :parameters (?top - item ?bottom - item ?l - location)
    :precondition (and (agent-at ?l) (holding ?top) (at ?bottom ?l) (clear ?bottom))
    :effect (and (on-top ?top ?bottom) (at ?top ?l) (clear ?top) (hand-empty)
                 (not (holding ?top)) (not (clear ?bottom)))
  )

  (:action unstack
    :parameters (?top - item ?bottom - item ?l - location)
    :precondition (and (agent-at ?l) (on-top ?top ?bottom) (at ?top ?l) (clear ?top) (hand-empty))
    :effect (and (holding ?top) (clear ?bottom)
                 (not (on-top ?top ?bottom)) (not (at ?top ?l)) (not (clear ?top)) (not (hand-empty)))
  )

  (:action slice-object
    :parameters (?i - item ?t - tool ?l - location)
    :precondition (and (agent-at ?l) (at ?i ?l) (has-tool ?t) (can-cut ?t) (whole ?i))
    :effect (and (cut-into-pieces ?i) (not (whole ?i)))
  )

  (:action take-photo
    :parameters (?i - item ?t - tool ?l - location)
    :precondition (and (agent-at ?l) (at ?i ?l) (has-tool ?t) (can-photo ?t))
    :effect (and (photo-taken ?i))
  )
)

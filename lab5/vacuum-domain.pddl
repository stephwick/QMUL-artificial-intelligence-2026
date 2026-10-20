(define (domain vacuum)
  (:requirements :strips :typing)
  (:types cell - object)
  (:predicates
    (robot-at ?c - cell)
    (dirty ?c - cell)
    (clean ?c - cell)                     ; STRIPS has no "not dirty": say what IS true
    (adjacent ?a - cell ?b - cell))

  (:action move
    :parameters (?from - cell ?to - cell)
    :precondition (and (robot-at ?from) (adjacent ?from ?to))
    :effect (and (robot-at ?to) (not (robot-at ?from))))

  (:action suck
    :parameters (?c - cell)
    :precondition (and (robot-at ?c) (dirty ?c))
    :effect (and (clean ?c) (not (dirty ?c))))
)

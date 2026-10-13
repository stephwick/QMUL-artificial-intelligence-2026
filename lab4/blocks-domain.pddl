(define (domain blocks)
  (:requirements :strips :typing)
  (:types block - object)

  (:predicates
    (on ?x - block ?y - block)     ; x sits directly on y
    (on-table ?x - block)
    (clear ?x - block)             ; nothing on top of x
    (holding ?x - block)
    (hand-empty))

  (:action pick-up
    :parameters (?x - block)
    :precondition (and (clear ?x) (on-table ?x) (hand-empty))
    :effect (and (holding ?x)
                 (not (on-table ?x)) (not (clear ?x)) (not (hand-empty))))

  (:action put-down
    :parameters (?x - block)
    :precondition (and (holding ?x))
    :effect (and (on-table ?x) (clear ?x) (hand-empty)
                 (not (holding ?x))))

  (:action unstack
    :parameters (?x - block ?y - block)
    :precondition (and (on ?x ?y) (clear ?x) (hand-empty))
    :effect (and (holding ?x) (clear ?y)
                 (not (on ?x ?y)) (not (clear ?x)) (not (hand-empty))))

  (:action stack
    :parameters (?x - block ?y - block)
    :precondition (and (holding ?x) (clear ?y))
    :effect (and (on ?x ?y) (clear ?x) (hand-empty)
                 (not (holding ?x)) (not (clear ?y))))
)

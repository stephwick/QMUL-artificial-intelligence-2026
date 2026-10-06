(define (problem two-animals)
  (:domain workshop)

  (:objects
    cat dog - item
    knife dslr - tool
    lab outdoors - location
  )

  (:init
    (agent-at lab) (hand-empty)
    (tool-at knife lab) (can-cut knife)
    (tool-at dslr lab)  (can-photo dslr)
    (at cat lab) (whole cat) (clear cat) (on-surface cat)
    (at dog lab) (whole dog) (clear dog) (on-surface dog)
  )

  (:goal (and (photo-taken cat) (cut-into-pieces dog) (at dog outdoors)))
)

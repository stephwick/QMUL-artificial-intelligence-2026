;;  init            goal
;;   C               A
;;   A   B           B
;;  -------          C
;;                 -------
(define (problem sussman)
  (:domain blocks)
  (:objects a b c - block)
  (:init (on c a) (on-table a) (on-table b)
         (clear c) (clear b) (hand-empty))
  (:goal (and (on a b) (on b c)))
)

;; Lab 1's TINY world:      #####
;;                          #A*.#
;;                          #..*#
;;                          #####
(define (problem tiny)
  (:domain vacuum)
  (:objects c11 c12 c13 c21 c22 c23 - cell)
  (:init
    (robot-at c11)
    (dirty c12) (dirty c23)
    (clean c11) (clean c13) (clean c21) (clean c22)
    (adjacent c11 c12) (adjacent c12 c11) (adjacent c12 c13) (adjacent c13 c12)
    (adjacent c21 c22) (adjacent c22 c21) (adjacent c22 c23) (adjacent c23 c22)
    (adjacent c11 c21) (adjacent c21 c11) (adjacent c12 c22) (adjacent c22 c12)
    (adjacent c13 c23) (adjacent c23 c13))
  (:goal (and (clean c11) (clean c12) (clean c13) (clean c21) (clean c22) (clean c23)))
)

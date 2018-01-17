;;; This file contains the definitions of objects, types and
;;; individuals that are used in the case scenarios of the Smarg Grid

(new-type {cable} {thing})
(new-split-subtypes {cable} 
		    '({cable underground} 
		      {cable in height}))

(new-indv {line 1} {cable in height})
(new-indv {line 2} {cable in height})
(new-indv {line 3} {cable in height})

(new-split '({movable object} {static object}))
(new-is-a {ground} {static object})
(new-is-a {cable} {movable object})

;; For the Smart Grids context, let's clasify objects in: ground
;; objects and high-rise.
(new-split-subtypes {undefined thing} 
		    '({underground} 
		      {ground object}
		      {high-rise object}))

(new-is-a {cable in height} {high-rise object})
(new-is-a {cable underground} {underground object})

(new-is-a {ground} {ground object})

(new-indv {loc at road} {place})
(new-indv {t_s 1} {time point})

(new-context {smart grid} {general})
(in-context {smart grid})
(new-indv {near} {measure})
(x-is-the-y-of-z {1} {measure magnitude} {near})
(x-is-the-y-of-z {km} {measure unit} {near})
(in-context {general})

(new-type {transportation} {thing})
(new-is-a {transportation} {movable object})
(new-type {car} {transportation})
;;; Some scone definitions for the Smart Grid case scenarios regarding
;;; spaces and locations. These definitions are going to be used to
;;; describe the space in which the scenarios are going to be framed.


(new-type {road} {land region})
(new-type {forest} {land region})
(new-type {dessert} {land region})

(new-is-a {city} {land region})
(new-is-a {sea} {water region})

(new-relation {pathway connecting}
	      :a-inst-of {geographical area}
	      :b-inst-of {geographical area} 
	      :c-inst-of {geographical area}
	      :symmetric t)

;(new-eq {is in contact with} {located at})

;;; Define some individuals for the case scenarios
(new-indv {City A} {city})
(new-indv {City B} {city})

(new-indv {Road AB} {pathway connecting} {City A} {City B})
(new-is-a {Road AB} {road})
(new-statement {City A} {area adjacent to} {road AB})
(new-statement {City B} {area adjacent to} {road AB})


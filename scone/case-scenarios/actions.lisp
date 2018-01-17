;;; Some scone definitions for the Smart Grid case scenarios regarding
;;; the actions that will be involved in the devised scenarios. 
;;; This file depends on the simple-episodic-model.lisp file, version 0.8.22

;; DEFINITIONS
(new-is-a {normal} {measure})
(new-is-a {dropped} {measure})

(new-indv {ground} {thing})

(new-type {short circuit} {event})
(new-type {start large load} {event})
(new-type {phase to phase} {event})
(new-type {phase to ground} {event})
(new-type {voltage sag} {event})


;; RELATIONS
(new-statement {short circuit} {causes} {voltage sag})
(new-statement {start large load} {causes} {voltage sag})
(new-statement {phase to phase} {causes} {short circuit})
(new-statement {phase to ground} {causes} {short circuit})

;; PULL TOGETHER ACTION
(in-context {general})
(new-action-type {pull together} 
		 :agent-type {animated object} 
		 :object-type {movable object}
		 :recipient-type {movable object})
(new-context {pull together BC} {general})
(new-is-a  {pull together BC} {before context})
(x-is-the-y-of-z {pull together BC} {before context} {pull together})
(new-context {pull together AC} {general})
(new-is-a  {pull together AC} {after context})
(x-is-the-y-of-z {pull together AC} {after context} {pull together})

(new-indv {pulled object 1} {object type})
(new-indv {pulled object 2} {object type})
;(new-split '({pulled object 1} {pulled object 2}))
(x-is-the-y-of-z  {pulled object 1} {action object} {pull together})
(x-is-the-y-of-z  {pulled object 2} {action object} {pull together})

(in-context {pull together BC})
(new-not-statement {pulled object 1} {is in contact with} {pulled object 2})
(new-not-eq {pulled object 1} {pulled object 2})
(statement-true? {pulled object 1} {is in contact with} {pulled object 2})
(in-context {pull together AC})
(new-statement {pulled object 1} {is in contact with} {pulled object 2})
(statement-true? {pulled object 1} {is in contact with} {pulled object 2})
(in-context {general})


;; VOLTAGE SAG
(in-context {general})

(new-context {voltage sag BC} {general})
(new-is-a  {voltage sag BC} {before context})
(x-is-the-y-of-z {voltage sag BC} {before context} {voltage sag})

(new-context {voltage sag AC} {general})
(new-is-a  {voltage sag AC} {after context})
(x-is-the-y-of-z {voltage sag AC} {after context} {voltage sag})
(new-indv-role {voltage measure} {voltage sag} {measure})

(in-context {voltage sag bc})
(x-is-the-y-of-z {normal} {voltage measure}  {voltage sag})

(in-context {voltage sag ac})
(x-is-the-y-of-z {dropped} {voltage measure}  {voltage sag})
(in-context {general})


;; PHASE TO GROUND

(in-context {general})
(new-context {phase to ground BC} {general})
(new-is-a {phase to ground BC} {before context})
(new-context {phase to ground AC} {general})
(new-is-a {phase to ground AC} {after context})
(x-is-the-y-of-z {phase to ground BC} {before context} {phase to ground})
(x-is-the-y-of-z {phase to ground AC} {after context} {phase to ground})

(new-indv-role {PtG cable line 1} {phase to phase} {cable})
(new-indv-role {PtG cable line 2} {phase to phase} {cable})
(new-indv-role {PtG cable line 3} {phase to phase} {cable})

(in-context {phase to ground BC})
(new-not-statement {lines} {is in contact with} {ground})
(in-context {phase to ground AC})
(new-statement {lines} {is in contact with} {ground})
(in-context {general})

;; SHIFT TOWARDS
(in-context {general})
(new-action-type {shift towards} 
		 :agent-type {animated object} 
		 :object-type {movable object})
(new-context {shift towards BC} {general})
(new-is-a {shift towards BC} {before context})
(new-context {shift towards AC} {general})
(new-is-a {shift towards AC} {after context})
(x-is-the-y-of-z {shift towards BC} {before context} {shift towards})
(x-is-the-y-of-z {shift towards AC} {after context} {shift towards})

(new-type-role {shifted object from} {action object} {place})
(new-type-role {shifted object to} {action object} {place})
(new-split '({shifted object from} {shifted object to}))


(in-context {shift towards AC})
(new-statement {action object} {located at} {shifted object from})

(in-context {shift towards BC})
(new-statement {action object} {located at} {shifted object to})

(in-context {general})

;; PHASE TO PHASE
;; Context declarations
(in-context {general})
(new-context {phase to phase BC} {general})
(new-is-a {phase to phase BC} {before context})
(new-context {phase to phase AC} {general})
(new-is-a {phase to phase AC} {after context})
(x-is-the-y-of-z {phase to phase BC} {before context} {phase to phase})
(x-is-the-y-of-z {phase to phase AC} {after context} {phase to phase})

;; Event role declarations
(new-type-role {PtP cable} {phase to phase} {cable} :n 3)
(new-indv-role {PtP cable line 1} {PtP cable}  {cable})
(new-indv-role {PtP cable line 2} {PtP cable}  {cable})
(new-indv-role {PtP cable line 3} {PtP cable}  {cable})

(new-type-role {PtP force applier} {phase to phase} {movable object})
(new-is-a {PtP force applier} {high-rise object})

;; Let's state what happen in every context
(in-context {phase to phase BC})
(new-not-statement {cable} {is in contact with} {cable})
(new-action {PtP force applier} {shift towards} {cable} {cable})

(in-context {phase to phase AC})
(new-statement {cable} {is in contact with} {cable})
(in-context {general})

(new-indv {voltage sag after PtP} {voltage sag})
(x-is-the-y-of-z {voltage sag after PtP} {subevent} {phase to phase} )

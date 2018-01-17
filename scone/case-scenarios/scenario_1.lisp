;; This file describes the effect that wind has on tree branches
;; We are modeling the bending moment of a tree branch which
;; determines when a branch is  going to break as a consequence of the
;; wind force

; Required relationships
(new-relation {status}
		       :a-inst-of {thing}
		       :b-inst-of {thing})

; Required types and individuals
(new-type {tree} {thing})
(new-type-role {branch} {tree} {thing})

; Required events and actions
(new-event-type {bend} '({event}))



;; First scenario -- broken branch because of wind
(new-event-type {bend until break tree branch} '({event} {bend})
			      	      :roles
				      ((:indv {bentBranch} {branch})
				       (:type {branchBendingRadious} {measure}))
  :throughout    
  ((defvar force) ;; N.m  m³/s
   (defvar branchRadious) ;; m
   (defvar t_s) ;; elapsed time in seconds
   (new-indv {instant-T0} {time point})
   (new-indv {instant-T1} {time point})
   (new-indv {instant-T2} {time point})
   (new-statement  {instant-T0} {before}  {instant-T1})
   (new-statement  {instant-T1} {before}  {instant-T2})
   ;(setq *current-time-point* {bend until break tree branch T1})
   (defvar bbr (lookup-element {branchBendingRadious}))
   (push-element-fluent bbr
			      	      :BendingMoment '(/ force (* bbr
			      	      (/ (*3.14 (expt branchRadious
			      	      4)) 4)))))
 
   :before
   ((in-context (new-context {bend until break tree branch bc} {general}))
    (setq *current-time-point* {bending tree branch T0})	
    (new-statement {bentBranch} {status} {unbent})
    (fluent-hold-at-time bbr :BendingMoment {instant-T0} 'unbent))
   :after
   ((in-context (new-context {bend until break tree branch ac} {general}))
    (setq *current-time-point* {instant-T1})
    (fluent-released bbr :BendingMoment '(/ force (* bbr
			      	      (/ (*3.14 (expt branchRadious
			      	      4)) 4))){instant-T1})
    (fluent-hold-at-time (lookup-element {branchBendingRadious})
			      	      :BendingMoment {instant-T2}
			      	      'broken t)))

(new-event-type {bending tree branch} '({event} {bend} {bend until break
			      	      tree branch})

   :throughout    
   ((in-context (new-context {bending tree branch tc} {bend until break
   tree branch tc}))
   (fluent-released (lookup-element {branchBendingRadious})
			      	      :BendingMoment  '(/ force (* bbr
			      	      (/ (*3.14 (expt branchRadious
			      	      4)) 4))) {instant-T1}))

   :after
   ((in-context (new-context {bending tree branch ac} {general}))
    (setq *current-time-point* {bend until break tree branch T2})
    (fluent-hold-at-time (lookup-element {branchBendingRadious})
			      	      :BendingMoment {instant-T2}
			      	      'unbent t)))

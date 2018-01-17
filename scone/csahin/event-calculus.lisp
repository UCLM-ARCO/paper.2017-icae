;; Fluent: a fluent represents a time-varying property of the world,
;; such as the location of a physical object 
(new-type {fluent} {thing})
(defvar *current-time-point*) 

(new-relation {holds at}
	      :a-inst-of {fluent}
	      :b-inst-of {time point})

(new-relation {releases at}
	      :a-inst-of {fluent}
	      :b-inst-of {time point})

;(set-element-fluent (lookup-element {lisa}) :status (format t "hello"))

(defmacro set-element-fluent (e fluent &optional (forms t))
"Set the FLUENT of element E as a changing property. Optionally, the
formulae that states how the fluent varies along the time can be
provided by stating FORMS" 
`(setf (getf (properties ,e) ,fluent) ,forms))

(defmacro get-element-fluent (e fluent &optional (time-point *current-time-point*))
  "Get the specified FLUENT of element E, by recalculanting
  the formula given by FORMS, or NIL if this property is
   not present."
  (if time-point
      (setq fluent (read-from-string (concatenate 'string (write-to-string						   fluent) "-at-"  (remove #\} (subseq  (write-to-string time-point) 1))))))
  `(getf (properties ,e) ,fluent))

(defmacro eval-element-fluent (e fluent)
  "Get and evaluate the function describing the FLUENT of element E"
  ;; TO-FIX: It has to be checked if the FLUENT value is a formulae or
  ;; it is just a constant value, since EVAL function throw an error
  ;; if it is not a list
  `(eval (getf (properties ,e) ,fluent)))

(defun push-element-fluent (e fluent form &optional  (already-logged nil))
  "The FLUENT of E should be a list. Push the FORM, that describes how
  the fluent varies along the time, onto this list. Create the fluentx
  as a property if it doesn't already exist."
  (prog1 
      (push form (getf (properties e) fluent)))
  (unless already-logged
    (kb-log "(push-element-fluent ~S '~S '~S)~%" e fluent form)))

(defun fluent-hold-at-time (e fluent time-point 
			       &optional (value t) (already-logged nil))
  "Represents that FLUENT does not change the value, and has a
  constant VALUE at TIME-POINT"
  (let ((nft 
	 (concatenate 'string "{" (subseq (write-to-string fluent) 1)
		      " of " (remove #\) (subseq (write-to-string
							  (lookup-element  e)) 8))))
	(e1 (eval e)))
    (if (not already-logged)
	(progn 
	  (set-element-fluent e1 fluent value)
	  (setq fluent (read-from-string (concatenate 'string
						      (write-to-string
						       fluent) "-at-"
						       (remove #\}
							       (subseq
								(write-to-string
								 time-point)
								1))))) 
	  (set-element-fluent e1 fluent value)
	  (new-statement (new-indv (read-from-string nft) {fluent})
			 {holds at} time-point))
	(progn
	  (set-element-fluent e1 fluent value)
	  (setq fluent (read-from-string (concatenate 'string
						      (write-to-string
						       fluent) "-at-"
						       (remove #\}
							       (subseq
								(write-to-string
								 time-point)
								1))))) 
	  (set-element-fluent e1 fluent value)
	  (new-statement (read-from-string nft) {holds at} time-point)))))


(defun fluent-released (e fluent &optional (form t) (time-point
  *current-time-point*))
  "Realeased from the common sense law of inertia, that states that
  things tend to reamin constant. This function releases FLUENT from
  that law, and when provided, states how FLUENT changes along the
  time"
  (let ((nft 
	 (concatenate 'string "{" (subseq (write-to-string fluent) 1)
		      " of " (remove #\) (subseq (write-to-string
							  (lookup-element
							   e)) 8)))))
    (if (or (statement-true? time-point {before} *current-time-point*)
	    (eq (lookup-element time-point) (lookup-element *current-time-point*)))
	(progn
	  (new-statement (read-from-string nft)  {releases at}
			 time-point)
	  (setf (getf (properties e) fluent) form)
	  ;(set-element-fluent e fluent form)
					;(remove-element (lookup-element (read-from-string nft)))
	  (setq fluent (read-from-string (concatenate 'string
						      (write-to-string
						       fluent) "-at-"
						       (remove #\}
							       (subseq
								(write-to-string
								 time-point)
								1))))) 
	  (format t "~S" fluent)
	  (setf (getf (properties e) fluent) form))
	(new-statement (read-from-string nft)  {releases at} time-point))))
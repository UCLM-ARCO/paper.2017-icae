;; added by mjsantof
(new-indv-role {object involved} {event} {thing})
(defvar *object-involved* (lookup-element {object involved}))
(defvar *before-context* (lookup-element {before context}))
(defvar *after-context* (lookup-element {after context}))
;; end of addition

(defmacro new-event-type (iname parents
				&key
				(context *context*)
				english
				roles
				throughout
				before
				after)
  "Creates a new event type with the given INAME and with parents PARENTS in context
   :CONTEXT. Sets the english external names to :ENGLISH. When :ROLES is supplied,
   creates the given roles in the throughout context of the event. Then executes the
   three bodies :THROUGHOUT, :BEFORE and :AFTER in the appropriate contexts. "
  
  (let ((event (gensym "event"))
	(curr-ctxt (gensym "curr-ctxt-"))
	(before-ctxt (gensym "before-context-"))
	(after-ctxt (gensym "after-context-"))
	(role-iname (gensym "role-iname-"))
	(role-args (gensym "role-args-")))
    (append
     `(progn
       
       ;; Check if all parents are events
       (dolist (p ,parents)
	 (unless (is-x-a-y? p *event*)
	   (error "~A is not an event." p)))
       
       (cond 
	 ;; If iname is in the kb, register the english names and create the IS-A links
	 ((lookup-element ,iname)
	  (when ,english (apply #'english ,iname ,english))
	  (dolist (p ,parents)
	    (new-is-a ,iname p :context ,context)))
	 
	 ;; if it's not and the first parent is an event, create a new type and create IS-A
	 ;; links between the rest
	 (t
	  (new-type ,iname (car ,parents) :english ,english :context ,context)
	  (dolist (p (cdr ,parents))
	    (new-is-a ,iname p :context ,context)))))
     
     ;; At this point iname is in the kb and the english names are registered
     (list
      (append
       `(let* ((,event (lookup-element ,iname))
	       (,curr-ctxt *context*)
	       (,before-ctxt (the-x-role-of-y *before-context* ,event))
	       (,after-ctxt (the-x-role-of-y *after-context* ,event))))

       ;; we're in the given context
       (list `(in-context ,context))
       ;; let the before context inherit from the given context
       (list `(new-is-a ,before-ctxt ,context))

       (list
	`(let ((,role-args nil)
	       (,role-iname nil))
	   
	   ;; create the roles
	   (dolist (role-des (quote ,roles))
	     (ecase (car role-des)
	       (:type
		;; push the possible keyword arguments
		(setq ,role-args (append (nthcdr 3 role-des) ,role-args))
		;; push the parent
		(push (third role-des) ,role-args)
		;; push the owner
		(push ,event ,role-args)
		;; push the iname
		(push (second role-des) ,role-args)
		(setq ,role-iname (second role-des))
		
		(apply 'new-type-role ,role-args)
		(x-is-a-y-of-z ,role-iname *object-involved* ,event))
	       
	       (:indv
		;; push the possible keyword arguments
		(setq ,role-args (append (nthcdr 3 role-des) ,role-args))
		;; push the parent
		(push (third role-des) ,role-args)
		;; push the owner
		(push ,event ,role-args)
		;; push the iname
		(push (second role-des) ,role-args)
		(setq ,role-iname (second role-des))
		
		(apply 'new-indv-role ,role-args)
		(x-is-a-y-of-z ,role-iname *object-involved* ,event))
	       
	       (:rename
		;; push the iname and possibly the english names
		(setq ,role-args (append (cddr role-des) ,role-args))
		;; push the :iname keyword
		(push ':iname ,role-args)
		;; push the owner
		(push ,event ,role-args)
		;; push the rolename
		(push (cadr role-des) ,role-args)
		
		(setq ,role-iname (apply 'create-the-x-role-of-y ,role-args))
		(unless ,role-iname
		  (error "~A is not a role of ~A.~%" ,role-iname ,event))
		(x-is-a-y-of-z ,role-iname *object-involved* ,event)))
	     (setq ,role-args nil))))
       
       ;; execute the throughout body
       throughout
       ;; execute the before body in the throughout context
       (list `(in-context ,before-ctxt))
       before
       ;; execute the after body in the after context
       (list `(in-context ,after-ctxt))
       after
       ;; switch to the original context
       (list `(in-context ,curr-ctxt)))))))


(defun new-event-indv (iname parent
			     &key
			     context
			     english)

  "Creates a new event individual with the given INAME and with parent PARENT.
   If :CONTEXT is given the new individual is created in that context. If :ENGLISH
   is given, registers them as external names for INAME."

  ;; find the parent
  (setq parent (lookup-element parent))
  ;; check if parent is an event type
  (unless (and (type-node? parent)
	       (is-x-a-y? parent *event*))
    (error "~A is not an event type.~%" parent))
  ;; create and return the new indv
  (new-indv iname parent :context context :english english))

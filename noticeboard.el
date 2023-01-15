;;; noticeboard.el --- interface to noticeboard hardware  -*- lexical-binding: t; -*-

;; Copyright (C) 2018, 2021, 2023  John Sturdy

;; Author: John Sturdy <john.sturdy@grapeshot.com>
;; Keywords: hardware

;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with this program.  If not, see <http://www.gnu.org/licenses/>.

;;; Commentary:

;; 

;;; Code:

(defvar noticeboard-controller-program
  "~/open-projects/github.com/hillwithsmallfields/noticeboard/noticeboard.py")

(defvar noticeboard-process nil)

(defun noticeboard-talkback (process string)
  "The monitor function for the noticeboard hardware talkback."
  (condition-case evar
      (eval string)
    (error (message "Problem in noticeboard talkback"))))

(defun noticeboard-start-process ()
  "Connect to the hardware control program on the noticeboard."
  ;; TODO: The user must be in a group that is allowed GPIO access?
  (setq noticeboard-process
	(start-process "noticeboard"
		       nil
		       (expand-file-name noticeboard-controller-program)))
  (set-process-filter noticeboard-process noticeboard-talkback))

(defun noticeboard-stop-process ()
  "Stop the noticeboard process."
  (interactive)
  (kill-process noticeboard-process)
  (setq noticeboard-process nil))

(defun noticeboard-restart-process ()
  "Kill and restart the noticeboard process."
  (interactive)
  (noticeboard-stop-process)
  (noticeboard-start-process))

(defun require-noticeboard-process ()
  "Start the hardware controller process if necessary."
  (unless noticeboard-process
    (connect-to-noticeboard)))

(defun noticeboard-command (command)
  "Send COMMAND to the noticeboard."
  (require-noticeboard-process)
  (process-send-string noticeboard-process command)  

(defun noticeboard-extend-keyboard ()
  "Extend the keyboard."
  (noticeboard-command "extend\n"))

(defun noticeboard-retract-keyboard ()
  "Retract the keyboard."
  (noticeboard-command "retract\n"))

(defun noticeboard-play (soundfile)
  "Play a sound file."
  (interactive "fPlay sound file: ")
  (noticeboard-command (format "play %s\n" soundfile)))

(defun noticeboard-say (text)
  "Play a sound file."
  (interactive "fSay text: ")
  (noticeboard-command (format "say \"%s\"\n" text)))

(defun noticeboard-shine ()
  "Switch the lights on."
  (interactive)
  (noticeboard-command "shine\n")

(defun noticeboard-quench ()
  "Switch the lights off."
  (interactive)
  (noticeboard-command "quench\n"))

(defun noticeboard-photo ()
  "Take a timestamped photo."
  (interactive)
  (noticeboard-command "photo\n")
    
(provide 'noticeboard)
;;; noticeboard.el ends here

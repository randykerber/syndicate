-- Export the raw source of the newest N messages of one Apple Mail mailbox to a
-- staging folder, one file per message (numbered; the Python side names them).
-- argv: account, mailbox NAME (bare — resolved anywhere in the account: the Hedgeye
--       mailboxes sit under a "Hedgeye" folder, ETF-weekly/ETF-Monthly under HE-ETF-Pro),
--       staging dir (POSIX path), limit (0 = every message)
-- Hand-run:
--   osascript export_mailbox.applescript iCloud HE-PS /tmp/stage 12
on run argv
	set acct to item 1 of argv
	set mbName to item 2 of argv
	set staging to item 3 of argv
	set lim to (item 4 of argv) as integer
	tell application "Mail"
		set theAcct to account acct
		set mb to missing value
		repeat with cand in (every mailbox of theAcct)
			if (name of cand) is mbName then
				set mb to cand
				exit repeat
			end if
		end repeat
		if mb is missing value then error "no mailbox named " & mbName & " in account " & acct
		set n to count of messages of mb
		if n = 0 then return "0"
		-- Mail returns messages in the mailbox's own order; find which end is newest
		set dFirst to date received of message 1 of mb
		set dLast to date received of message n of mb
		if lim = 0 or lim > n then set lim to n
		set idxs to {}
		if dFirst ≥ dLast then
			repeat with i from 1 to lim
				set end of idxs to i
			end repeat
		else
			repeat with i from n to (n - lim + 1) by -1
				set end of idxs to i
			end repeat
		end if
		set written to 0
		repeat with i in idxs
			set m to message i of mb
			set src to source of m
			set fp to staging & "/" & (i as text) & ".eml"
			set fh to open for access (POSIX file fp) with write permission
			set eof fh to 0
			write src to fh as «class utf8»
			close access fh
			set written to written + 1
		end repeat
		return written as text
	end tell
end run

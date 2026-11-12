-- The account vault (Jay, 2026-11-12: "a banker npc that can store gold between all accounts"): gold any character on
-- the same account can reach, at any banker. A character's own bank balance still works as in Tibia (deposit, withdraw,
-- transfer); the vault sits on top of it: "vault", "vault deposit 500", "vault withdraw 500".
SpireVault = {}

local function store()
	return kv.scoped("spirebound-vault")
end

function SpireVault.balance(accountId)
	return tonumber(store():get(tostring(accountId)) or 0) or 0
end

function SpireVault.set(accountId, amount)
	store():set(tostring(accountId), math.max(0, math.floor(amount)))
end

-- Pure: parse "vault deposit 500" / "vault withdraw all" -> action, amount ("all" -> -1); nil if not a vault command
function SpireVault.parse(msg)
	local lower = msg:lower()
	if not lower:find("vault", 1, true) then
		return nil
	end
	local action = lower:find("deposit", 1, true) and "deposit" or lower:find("withdraw", 1, true) and "withdraw" or "show"
	local n = tonumber(lower:match("(%d+)"))
	if lower:find("all", 1, true) then
		n = -1
	end
	return action, n
end

-- Pure: move gold between a bank balance and the vault. Returns newBank, newVault, message
function SpireVault.move(action, amount, bank, vault)
	if action == "show" then
		return bank, vault, string.format("Your account vault holds %d gold. Every character on your account can use it. Say 'vault deposit <amount>' or 'vault withdraw <amount>'.", vault)
	end
	if not amount then
		return bank, vault, "How much? Say for example 'vault deposit 1000'."
	end
	if action == "deposit" then
		local n = amount < 0 and bank or amount
		if n <= 0 or n > bank then
			return bank, vault, "Your bank balance doesn't hold that much."
		end
		return bank - n, vault + n, string.format("%d gold moved into your account vault. It now holds %d.", n, vault + n)
	end
	local n = amount < 0 and vault or amount
	if n <= 0 or n > vault then
		return bank, vault, "Your account vault doesn't hold that much."
	end
	return bank + n, vault - n, string.format("%d gold moved from your account vault to your bank balance.", n)
end

-- NPC hook for bankers: true when handled
function SpireVault.talk(npc, npcHandler, player, msg)
	local action, amount = SpireVault.parse(msg)
	if not action then
		return false
	end
	local acc = player:getAccountId()
	local bank, vault, text = SpireVault.move(action, amount, player:getBankBalance(), SpireVault.balance(acc))
	player:setBankBalance(bank)
	SpireVault.set(acc, vault)
	npcHandler:say(text, npc, player)
	return true
end

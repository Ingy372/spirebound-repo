-- In-game Memorial and leaderboards (DESIGN.md 5.5, 13). Roadmap 6.2.
SpireBoards = { TOP = 20, SCAN = 300 }

-- Pure: Memorial records (name -> {level, vocation, cause, time}) to sorted lines, highest level first
function SpireBoards.memorialLines(records)
	local list = {}
	for name, r in pairs(records or {}) do
		table.insert(list, { name = name, level = r.level or 0, vocation = r.vocation or "?", cause = r.cause or "unknown", time = r.time or 0 })
	end
	table.sort(list, function(a, b)
		if a.level ~= b.level then
			return a.level > b.level
		end
		return a.time < b.time
	end)
	local lines = {}
	for i, r in ipairs(list) do
		lines[i] = string.format("%d. %s, level %d %s - fell to %s (%s)", i, r.name, r.level, r.vocation, r.cause, os.date("%Y-%m-%d", r.time))
	end
	return lines
end

-- Pure: rows {name, level, vocation, mode, retired} already sorted by experience -> board lines.
-- mode filter: nil = everyone, or a difficulty number. Retired Death Game characters are marked.
function SpireBoards.rankLines(rows, mode, limit)
	local lines = {}
	for _, r in ipairs(rows) do
		if not mode or r.mode == mode then
			local mark = r.retired and " [fallen]" or ""
			local tag = (not mode and r.mode == 3) and " (Death Game)" or ((not mode and r.mode == 2) and " (Hardcore)" or "")
			table.insert(lines, string.format("%d. %s, level %d %s%s%s", #lines + 1, r.name, r.level, r.vocation, tag, mark))
			if #lines >= (limit or SpireBoards.TOP) then
				break
			end
		end
	end
	return lines
end

-- Read all Memorial records
function SpireBoards.memorial()
	local store = kv.scoped("spirebound-memorial")
	local out = {}
	for _, name in ipairs(store:keys() or {}) do
		out[name] = store:get(name)
	end
	return out
end

-- Top characters by experience (offline ones too), with their difficulty from the KV store
function SpireBoards.rows()
	local rows = {}
	local q = db.storeQuery("SELECT `id`, `name`, `level`, `vocation` FROM `players` WHERE `group_id` < 4 ORDER BY `experience` DESC LIMIT " .. SpireBoards.SCAN)
	if not q then
		return rows
	end
	repeat
		local guid = Result.getNumber(q, "id")
		local pk = kv.scoped("player"):scoped(tostring(guid)):scoped("spirebound")
		local voc = Vocation(Result.getNumber(q, "vocation"))
		table.insert(rows, {
			name = Result.getString(q, "name"),
			level = Result.getNumber(q, "level"),
			vocation = voc and voc:getName() or "None",
			mode = pk:get("difficulty") or 1,
			retired = pk:get("retired") == true,
		})
	until not Result.next(q)
	Result.free(q)
	return rows
end

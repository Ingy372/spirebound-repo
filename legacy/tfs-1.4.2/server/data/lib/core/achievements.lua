--[[
Functions:
	getAchievementInfoById(achievement_id)
	getAchievementInfoByName(achievement_name)
	getSecretAchievements()
	getPublicAchievements()
	getAchievements()
	Player:addAchievement(achievement_id/name[, hideMsg])
	Player:removeAchievement(achievement_id/name)
	Player:hasAchievement(achievement_id/name)
	Player:addAllAchievements([hideMsg])
	Player:removeAllAchievements()
	Player:getSecretAchievements()
	Player:getPublicAchievements()
	Player:getAchievements()
	isAchievementSecret(achievement_id/name)
	Player:getAchievementPoints()
	Player:addAchievementProgress()
Storages:
	PlayerStorageKeys.achievementsBase -- base storage
	PlayerStorageKeys.achievementsCounter -- this storage will be used to save the process to obtain the certain achievement
	(Ex: this storage + the id of achievement 'Allowance Collector' to save how many piggy banks has been broken
]]

-- Spirebound: the upstream TFS achievement list (CipSoft content) was removed.
-- Spirebound titles and accolades are its own system (05, 13); this keeps the engine API working.
achievements = {}

ACHIEVEMENT_FIRST = 1
ACHIEVEMENT_LAST = #achievements

function getAchievementInfoById(id)
	for k, v in pairs(achievements) do
		if k == id then
			local targetAchievement = {}
			targetAchievement.id = k
			targetAchievement.actionStorage = PlayerStorageKeys.achievementsCounter + k
			for inf, it in pairs(v) do
				targetAchievement[inf] = it
			end
			return targetAchievement
		end
	end
	return false
end

function getAchievementInfoByName(name)
	for k, v in pairs(achievements) do
		if v.name:lower() == name:lower() then
			local targetAchievement = {}
			targetAchievement.id = k
			targetAchievement.actionStorage = PlayerStorageKeys.achievementsCounter + k
			for inf, it in pairs(v) do
				targetAchievement[inf] = it
			end
			return targetAchievement
		end
	end
	return false
end

function getSecretAchievements()
	local targetAchievement = {}
	for k, v in pairs(achievements) do
		if v.secret then
			targetAchievement[#targetAchievement + 1] = k
		end
	end
	return targetAchievement
end

function getPublicAchievements()
	local targetAchievement = {}
	for k, v in pairs(achievements) do
		if not v.secret then
			targetAchievement[#targetAchievement + 1] = k
		end
	end
	return targetAchievement
end

function getAchievements()
	return achievements
end

function isAchievementSecret(ach)
	local achievement
	if tonumber(ach) ~= nil then
		achievement = getAchievementInfoById(ach)
	else
		achievement = getAchievementInfoByName(ach)
	end
	if not achievement then
		print("[!] -> Invalid achievement \"" .. ach .. "\".")
		return false
	end

	return achievement.secret
end

function Player.hasAchievement(self, ach)
	local achievement
	if tonumber(ach) ~= nil then
		achievement = getAchievementInfoById(ach)
	else
		achievement = getAchievementInfoByName(ach)
	end
	if not achievement then
		print("[!] -> Invalid achievement \"" .. ach .. "\".")
		return false
	end

	return self:getStorageValue(PlayerStorageKeys.achievementsBase + achievement.id) > 0
end

function Player.getAchievements(self)
	local targetAchievement = {}
	for k = 1, #achievements do
		if self:hasAchievement(k) then
			targetAchievement[#targetAchievement + 1] = k
		end
	end
	return targetAchievement
end

function Player.addAchievement(self, ach, hideMsg)
	local achievement
	if tonumber(ach) ~= nil then
		achievement = getAchievementInfoById(ach)
	else
		achievement = getAchievementInfoByName(ach)
	end
	if not achievement then
		print("[!] -> Invalid achievement \"" .. ach .. "\".")
		return false
	end

	if not self:hasAchievement(achievement.id) then
		self:setStorageValue(PlayerStorageKeys.achievementsBase + achievement.id, 1)
		if not hideMsg then
			self:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Congratulations! You earned the achievement \"" .. achievement.name .. "\".")
		end
	end
	return true
end

function Player.removeAchievement(self, ach)
	local achievement
	if tonumber(ach) ~= nil then
		achievement = getAchievementInfoById(ach)
	else
		achievement = getAchievementInfoByName(ach)
	end
	if not achievement then
		print("[!] -> Invalid achievement \"" .. ach .. "\".")
		return false
	end

	if self:hasAchievement(achievement.id) then
		self:setStorageValue(PlayerStorageKeys.achievementsBase + achievement.id, -1)
	end
	return true
end

function Player.addAllAchievements(self, hideMsg)
	for i = ACHIEVEMENT_FIRST, ACHIEVEMENT_LAST do
		self:addAchievement(i, hideMsg)
	end
	return true
end

function Player.removeAllAchievements(self)
	for k = 1, #achievements do
		if self:hasAchievement(k) then
			self:removeAchievement(k)
		end
	end
	return true
end

function Player.getSecretAchievements(self)
	local targetAchievement = {}
	for k, v in pairs(achievements) do
		if self:hasAchievement(k) and v.secret then
			targetAchievement[#targetAchievement + 1] = k
		end
	end
	return targetAchievement
end

function Player.getPublicAchievements(self)
	local targetAchievement = {}
	for k, v in pairs(achievements) do
		if self:hasAchievement(k) and not v.secret then
			targetAchievement[#targetAchievement + 1] = k
		end
	end
	return targetAchievement
end

function Player.getAchievementPoints(self)
	local points = 0
	local list = self:getAchievements()
	if #list > 0 then -- has achievements
		for i = 1, #list do
			local targetAchievement = getAchievementInfoById(list[i])
			if targetAchievement.points > 0 then -- avoid achievements with unknow points
				points = points + targetAchievement.points
			end
		end
	end
	return points
end

function Player.addAchievementProgress(self, ach, value)
	local achievement = tonumber(ach) ~= nil and getAchievementInfoById(ach) or getAchievementInfoByName(ach)
	if not achievement then
		print('[!] -> Invalid achievement "' .. ach .. '".')
		return true
	end

	local storage = PlayerStorageKeys.achievementsCounter + achievement.id
	local progress = self:getStorageValue(storage)
	if progress < value then
		self:setStorageValue(storage, math.max(1, progress) + 1)
	elseif progress == value then
		self:setStorageValue(storage, value + 1)
		self:addAchievement(achievement.id)
	end
	return true
end

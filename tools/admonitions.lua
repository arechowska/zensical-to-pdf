-- admonitions.lua: конвертирует MkDocs !!! блоки в blockquote для PDF
-- и убирает внутренние .md-ссылки (они ведут на localhost в PDF)

function Link(el)
    local target = el.target or ""
    -- внутренние ссылки: .md файлы, якоря (#...) или localhost
    if target:match("%.md") or target:match("^#") or target:match("localhost") then
        return el.content  -- оставляем только текст ссылки
    end
end

-- Типы admonitions → заголовок по умолчанию
local ADMONITION_LABELS = {
    note = "Примечание", info = "Информация", tip = "Совет",
    warning = "Внимание", danger = "Опасность", success = "Успешно",
    example = "Пример", question = "Вопрос", quote = "Цитата",
}

function Para(el)
    local first = el.content[1]
    if not (first and first.t == "Str" and first.text == "!!!") then
        return nil
    end

    local admonition_type = ""
    local title = {}
    local body = {}
    local state = "prefix"

    for _, item in ipairs(el.content) do
        if state == "prefix" then
            if item.t == "Str" and item.text ~= "!!!" then
                -- тип: note, warning, info и т.д.
                admonition_type = item.text:lower():gsub('"', '')
                if item.text:find('"') or item.text:find('\u{201C}') then
                    state = "title"
                    local text = item.text:gsub('[%"%\u{201C}]', '')
                    if #text > 0 then table.insert(title, pandoc.Str(text)) end
                else
                    state = "maybe_title"
                end
            end
        elseif state == "maybe_title" then
            if item.t == "Str" and (item.text:find('"') or item.text:find('\u{201C}')) then
                state = "title"
                local text = item.text:gsub('[%"%\u{201C}]', '')
                if #text > 0 then table.insert(title, pandoc.Str(text)) end
            elseif item.t == "Quoted" then
                for _, q in ipairs(item.content) do table.insert(title, q) end
                state = "body"
            elseif item.t ~= "Space" then
                table.insert(body, item)
                state = "body"
            end
        elseif state == "title" then
            if item.t == "Str" and (item.text:find('"') or item.text:find('\u{201D}')) then
                local t = item.text:gsub('[%"%\u{201D}]', '')
                if #t > 0 then table.insert(title, pandoc.Str(t)) end
                state = "body"
            else
                table.insert(title, item)
            end
        else
            table.insert(body, item)
        end
    end

    while body[1] and (body[1].t == "Space" or body[1].t == "SoftBreak") do
        table.remove(body, 1)
    end

    -- Если заголовок не задан — использовать метку по типу
    if #title == 0 then
        local label = ADMONITION_LABELS[admonition_type] or admonition_type
        if #label > 0 then
            title = {pandoc.Str(label)}
        end
    end

    local result = {}
    if #title > 0 then
        table.insert(result, pandoc.Strong(title))
        table.insert(result, pandoc.Str(":"))
        table.insert(result, pandoc.Space())
    end
    for _, item in ipairs(body) do
        table.insert(result, item)
    end

    if #result > 0 then
        return pandoc.BlockQuote({pandoc.Para(result)})
    end
    return pandoc.Null()
end

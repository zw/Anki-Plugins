HL_FORMAT = "<span style='color:blue; font-weight:bold;'>%s</span>"

function hl(text)
    return string.format(HL_FORMAT, text)
end

function hlCaps(text)
    result, numberOfSubs = string.gsub(text, '(%u+)', hl)
    return result
end

function noteStyle(text)
    -- We'd like to support markdown within the div despite Markdown saying
    -- it's ignored within block-level elements.  Python Markdown seems to
    -- half-ignore it, by treating the div markup itself as content but not
    -- ignoring what's enclosed.  A workaround for styling a list is to make
    -- the div appear to be a paragraph to Python Markdown, although that tends
    -- to cause insertion of superfluous newlines.  Ideally one day PM will
    -- support the PHP Markdown Extra attribute that addresses this problem:
    --   http://michelf.com/projects/php-markdown/extra/#markdown-attr
    return "<div style='font-style:italic;'>\n\n" .. text .. "\n</div>"
end

-- Referencing
function initRefs()
        refs = {}
        numRefs = 0
end

table.insert(BEGIN_CARD, initRefs)

function ref(text, symbol, link)
        text = text or ""
        symbol = symbol or ""
        link = link or ""

        -- Record and autonumber this reference.
        if symbol == "" then
            table.insert(refs, {["text"] = text, ["link"] = link})
            numRefs = numRefs + 1
            symbol = numRefs
        end

        -- small is a hack around Qt's limited CSS support; see http://tinyurl.com/yeuthno
        -- would rather use 'em's to measure font relatively
        LINKED_SYMBOL_STYLE = "<a href='%s'>%s</a>"
        REF_STYLE = "<span %s style='font-weight:bold; vertical-align:super; font-size:small; '>[%s]</span>"
        TEXT_ATTR = 'title="%s"'
        
        if text == "" then
            text_attr = ""
        else
            text_attr = string.format(TEXT_ATTR, text)
        end

        if link == "" then
                symbol_html = symbol
        else
                symbol_html = string.format(LINKED_SYMBOL_STYLE, link, symbol)
        end

        formatted = string.format(REF_STYLE, text_attr, symbol_html)
        return formatted
end

-- Legacy.
function fixme(link)
        return ref("FIXME", "???", link)
end
function note(short, long, link)
        return ref(long, short, link)
end
-- end legacy

-- For explanatory text (not required for a correct answer to the card) that
-- needs to be anchored to a particular point in the answer to make sense, and
-- can't just float in the notes field (or, could but would require too much
-- context).
function extra(text, link)
        return ref(text, nil, link)
end

function printRefs()
        ret = ""

        if # refs == 0 then
            --return ret
            return "no refs to print"
        end
        ret = ret .. "References:\n"
        ret = ret .. "\n"
        for _,v in ipairs(refs) do
                ret = ret .. "1. " .. v["text"]
                if v["link"] ~= "" then
                    ret = ret .. " <a href='" .. v["link"] .. "'>(link)</a>"
                end
                ret = ret .. "\n"
        end
        return ret
end


function latin(text)
        LATIN_STYLE = "<i>%s</i>"
        return string.format(LATIN_STYLE, text)
end


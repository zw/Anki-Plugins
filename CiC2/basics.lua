ANSWER_FORMAT = "<span style='color:blue; font-weight:bold;'>%s</span>"

function a(text)
    if CiC.QorA == "answer" then
        return string.format(ANSWER_FORMAT, text)
    end
    return text
end

function ifnem(text, fmt)
    if text ~= "" then
        return string.format(fmt, text)
    end
    return ""
end

function ifem(text, ifEmpty, ifNonEmpty)
    ifNonEmpty = ifNonEmpty or ""
    if text == "" then
        return ifEmpty
    else
        return ifNonEmpty
    end
end

function ifa(text)
    if CiC.QorA == "answer" then
        return text
    end
    return ""
end

function ifq(text)
    if CiC.QorA == "question" then
        return text
    end
    return ""
end

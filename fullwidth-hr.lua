-- Pandoc Lua filter for nicer PDF tables/rules:
-- 1) Make HorizontalRule (---) span full text width
-- 2) Force sensible column widths (avoid overflow of long \texttt ids)
-- 3) Add \hline between table body rows (pandoc default has none)
-- 4) Allow breaks inside inline code (underscores / hyphens)

function Meta(meta)
  if not (FORMAT:match("latex") or FORMAT == "pdf") then
    return nil
  end
  local header = [[
\usepackage{xurl}
\Urlmuskip=0mu plus 1mu
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
]]
  local existing = meta["header-includes"]
  local block = pandoc.RawBlock("latex", header)
  if existing == nil then
    meta["header-includes"] = pandoc.MetaList({ pandoc.MetaBlocks({ block }) })
  else
    if existing.t ~= "MetaList" then
      existing = pandoc.MetaList({ existing })
    end
    existing:insert(pandoc.MetaBlocks({ block }))
    meta["header-includes"] = existing
  end
  return meta
end

function HorizontalRule()
  if not (FORMAT:match("latex") or FORMAT == "pdf") then
    return nil
  end
  return pandoc.RawBlock("latex", "\\noindent\\rule{\\textwidth}{0.4pt}")
end

-- Breakable monospace for long identifiers (avoids column overlap)
function Code(el)
  if not (FORMAT:match("latex") or FORMAT == "pdf") then
    return nil
  end
  -- \path from xurl allows breaks at _, -, /, .
  return pandoc.RawInline("latex", "\\path{" .. el.text .. "}")
end

local function prepend_hline(cell)
  if not cell then
    return
  end
  if not cell.contents or #cell.contents == 0 then
    cell.contents = { pandoc.Plain({ pandoc.RawInline("latex", "\\hline\n") }) }
    return
  end
  local first = cell.contents[1]
  if first.t == "Plain" or first.t == "Para" then
    table.insert(first.content, 1, pandoc.RawInline("latex", "\\hline\n"))
  else
    table.insert(cell.contents, 1, pandoc.Plain({ pandoc.RawInline("latex", "\\hline\n") }))
  end
end

local function set_col_widths(tbl)
  local n = #tbl.colspecs
  local widths
  if n == 2 then
    -- Skill | 作用
    widths = { 0.40, 0.60 }
  elseif n == 3 then
    -- 类别 | id | 说明 — give id room so long names wrap instead of overlapping
    widths = { 0.16, 0.44, 0.40 }
  else
    return
  end
  for i, w in ipairs(widths) do
    local align = tbl.colspecs[i][1]
    tbl.colspecs[i] = { align, w }
  end
end

function Table(tbl)
  if not (FORMAT:match("latex") or FORMAT == "pdf") then
    return nil
  end
  set_col_widths(tbl)
  for _, body in ipairs(tbl.bodies) do
    for i = 2, #body.body do
      prepend_hline(body.body[i].cells[1])
    end
  end
  return tbl
end
